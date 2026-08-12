# Deploying to Fly.io

The app deploys as a **single** Fly app, `wmf-scraper`, in the `ams` region.
FastAPI serves the JSON API under `/api` and the compiled React frontend from
the same process, so there is no second app and no CORS.

## Does the existing database survive this refactor?

**Yes.** Nothing about the data changes:

| | before | after |
| --- | --- | --- |
| Fly app | `wmf-scraper` | `wmf-scraper` (unchanged) |
| Volume | `wmf_data` | `wmf_data` (unchanged) |
| Mount point | `/data` | `/data` (unchanged) |
| `DATABASE_PATH` | `/data/wmf_scraper.db` | `/data/wmf_scraper.db` (unchanged) |
| Table schema | — | unchanged |

A `fly deploy` replaces the machine's *image*, not its volume. The volume is
re-attached to the new machine and the same SQLite file is opened in place.

Two things are worth knowing:

* `create_all()` now runs on every startup instead of only when the database
  file is missing. It is a no-op for tables that already exist and never drops
  or alters anything, so existing rows are untouched.
* The `wmf-scraper-front` app has **no volume**; destroying it cannot affect the
  data.

Take a snapshot first anyway — it costs nothing and takes seconds.

## Procedure

### 1. Authenticate

```bash
flyctl auth login              # or: export FLY_API_TOKEN=$(op read "op://HABCompTool/wmf_fly_token/password")
flyctl auth whoami
```

### 2. Back the database up

```bash
# Server-side snapshot of the volume.
fly volumes list -a wmf-scraper                         # note the volume id (vol_...)
fly volumes snapshots create <volume-id>
fly volumes snapshots list <volume-id>

# And a local copy, so the backup does not live only inside Fly.
fly ssh sftp get /data/wmf_scraper.db ./wmf_scraper.backup.db -a wmf-scraper
sqlite3 wmf_scraper.backup.db "select count(*) from taskresultmodel;"
```

### 3. Set the secrets

The frontend no longer carries any credentials, so all of these are now
server-side only. Setting secrets restarts the app, so do this before deploying.

```bash
fly secrets set -a wmf-scraper \
  SESSION_SECRET="$(openssl rand -hex 32)" \
  ADMIN_USERNAME='...' \
  ADMIN_PASSWORD='...' \
  SUPERADMIN_USERNAME='...' \
  SUPERADMIN_PASSWORD='...' \
  API_KEY='...'
```

`API_KEY` is optional and only enables `Authorization: Bearer` access for
scripts. If you no longer need it: `fly secrets unset API_KEY -a wmf-scraper`.

The app refuses to boot in production without `SESSION_SECRET` and at least one
username/password pair, and logs which one is missing.

### 4. Deploy

```bash
fly deploy
```

The build is entirely inside the Dockerfile: Node builds the frontend, uv
installs the Python dependencies from `uv.lock`, and the runtime stage carries
only the virtualenv and the compiled assets.

### 5. Verify

```bash
curl -s https://wmf-scraper.fly.dev/api/version
curl -s -o /dev/null -w '%{http_code}\n' https://wmf-scraper.fly.dev/api/competition/get_all_competitions   # expect 401
curl -s -o /dev/null -w '%{http_code}\n' https://wmf-scraper.fly.dev/                                       # expect 200, the UI
```

Then open <https://wmf-scraper.fly.dev/>, log in, and confirm a competition's
overall results still render — that proves the volume came back with its data.

### 6. The old frontend app

`wmf-scraper-front` no longer exists — it was already destroyed before the
v3.0.0 deploy, and `fly apps list` shows `wmf-scraper` as the only app in the
org. Nothing further to do.

If anyone still has <https://wmf-scraper-front.fly.dev> bookmarked, that URL is
dead. The app lives at <https://wmf-scraper.fly.dev>.

## Operational notes

* **One machine only.** A Fly volume attaches to a single machine, and the
  database is a file on it. Do not scale this app past one machine.
* **Restoring a snapshot:** `fly volumes create wmf_data --snapshot-id <id> -r ams -a wmf-scraper`,
  then attach it to a fresh machine.
* **Logs:** `fly logs -a wmf-scraper`. **Shell:** `fly ssh console -a wmf-scraper`.
