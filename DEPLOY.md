# Deploying to Fly.io

The app runs as a **single** Fly app, `wmf-scraper`, in `ams`. One FastAPI
process serves the JSON API under `/api` and the compiled React frontend from
the same origin, so there is no second app and no CORS.

Live at <https://wmf-scraper.fly.dev>.

| | |
| --- | --- |
| Fly app | `wmf-scraper` |
| Region | `ams` |
| Machines | exactly **one** (see [One machine only](#one-machine-only)) |
| Volume | `wmf_data`, 1 GB, mounted at `/data` |
| Database | `/data/wmf_scraper.db` (SQLite) |
| Health check | `GET /api/version` |

## Releasing

The normal path is a tag push.

```bash
make bump-patch                          # or bump-minor / bump-major
git commit -am "Release v$(make -s version)"
make tag
git push origin master
git push origin "v$(make -s version)"    # this triggers the deploy
```

[`.github/workflows/release.yml`](.github/workflows/release.yml) then verifies
the tag matches the committed version, deploys, polls `/api/version` until it
reports the new version, and opens a GitHub release. It is the only workflow in
the repository and runs no tests, so run `make check` before you tag.

It needs one repository secret:

| Secret | How to get it |
| --- | --- |
| `FLY_API_TOKEN` | `fly tokens create deploy -a wmf-scraper` |

The application secrets below live on Fly and are never read by CI.

### Deploying by hand

```bash
fly deploy          # or: make deploy
```

Useful when you are debugging. It skips every check the workflow runs, and the
deployed version will be whatever `pyproject.toml` currently says.

## Application secrets

Set on Fly, not in the repository. The app **refuses to start** in production
without `SESSION_SECRET` and at least one username/password pair, and logs
exactly which one is missing.

```bash
fly secrets set -a wmf-scraper \
  SESSION_SECRET="$(openssl rand -hex 32)" \
  ADMIN_USERNAME='...' \
  ADMIN_PASSWORD='...' \
  SUPERADMIN_USERNAME='...' \
  SUPERADMIN_PASSWORD='...' \
  API_KEY='...'
```

`API_KEY` is optional; it only enables `Authorization: Bearer` access for
scripts, with the `superadmin` role. Remove it with
`fly secrets unset API_KEY -a wmf-scraper`.

Setting a secret restarts the machine. Use `--stage` to hold the change until
the next deploy.

## The database

`fly deploy` replaces the machine's *image*, not its volume. The volume is
re-attached to the new machine and the same SQLite file is opened in place, so
deploys do not touch the data.

`SQLModel.metadata.create_all()` runs on every startup. It creates missing
tables and is a no-op for tables that already exist; it never drops or alters
anything.

### Backing up

Both, before anything risky:

```bash
# Server-side snapshot of the volume.
fly volumes list -a wmf-scraper                  # note the volume id (vol_...)
fly volumes snapshots create <volume-id>
fly volumes snapshots list <volume-id>

# And a local copy, so the backup does not live only inside Fly.
fly ssh sftp get /data/wmf_scraper.db ./backups/wmf_scraper.backup.db -a wmf-scraper
sqlite3 ./backups/wmf_scraper.backup.db "pragma integrity_check; select count(*) from taskresultmodel;"
```

Fly keeps daily snapshots with 5-day retention automatically. `backups/` is
gitignored.

### Restoring

```bash
fly volumes create wmf_data --snapshot-id <snapshot-id> -r ams -a wmf-scraper
```

then attach it to a fresh machine. To restore just the file, `fly ssh sftp
shell -a wmf-scraper` and put it back at `/data/wmf_scraper.db` while the app
is stopped.

### One machine only

A Fly volume attaches to a single machine and the database is a file on it.
**Do not scale this app past one machine** — a second machine would come up
with no volume, or with a different copy of the data.

## Verifying a deploy

```bash
curl -s https://wmf-scraper.fly.dev/api/version
curl -s -o /dev/null -w '%{http_code}\n' https://wmf-scraper.fly.dev/                                      # 200, the UI
curl -s -o /dev/null -w '%{http_code}\n' https://wmf-scraper.fly.dev/api/competition/get_all_competitions  # 401
```

Then log in and open a competition's overall results, which proves the volume
came back with its data.

## Operations

| | |
| --- | --- |
| Logs | `fly logs -a wmf-scraper` |
| Shell | `fly ssh console -a wmf-scraper` |
| Status | `fly status -a wmf-scraper` |
| Secrets | `fly secrets list -a wmf-scraper` |

The machine has `auto_stop_machines = 'stop'` and `min_machines_running = 0`,
so it sleeps when idle. The first request after a sleep waits a few seconds for
it to boot — that now delays the page load too, since the UI is served by the
same machine.
