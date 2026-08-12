<p align="center">
    <img src="assets/wmf.png" width="200" alt="WMF Scraper"/>
</p>

<h2 align="center" style="border-bottom: none;">WMF Scraper</h2>

<p align="center">
Fullstack app that scrapes, stores and analyses hot air balloon competition
results from <a href="https://www.watchmefly.net">WatchMeFly</a>.
</p>

A FastAPI backend serves both the JSON API (under `/api`) and the compiled React
frontend, from a **single** process and a **single** Fly.io app.

```
├── backend/
│   ├── wmf_scraper/        FastAPI application package
│   │   ├── actions/        business logic over the database
│   │   ├── models/         SQLModel tables and API schemas
│   │   ├── parsers/        WatchMeFly HTML scraping
│   │   ├── routers/        HTTP endpoints
│   │   ├── database.py     SQLite engine + session handling
│   │   ├── security.py     session cookies, API key, roles
│   │   └── settings.py     all environment variable access
│   └── tests/
├── frontend/               React 18 + TypeScript, built with Vite
│   └── src/
│       ├── components/     one component per screen
│       ├── config/api.ts   the shared axios client
│       └── hooks/          useVersion
├── scripts/sync_version.py keeps package.json in step with pyproject.toml
├── seed/                   request bodies for the bulk endpoints
├── .github/workflows/      release.yml, the only workflow: deploys a v* tag
├── pyproject.toml          Python project and version, managed with uv
├── Dockerfile              builds frontend + backend into one image
└── fly.toml                the single `wmf-scraper` app
```

## Requirements

* [uv](https://docs.astral.sh/uv/) for Python
* Node.js 22+ for the frontend
* [flyctl](https://fly.io/docs/flyctl/install/) to deploy

## Getting started

```bash
make install          # uv sync + npm ci
cp .env.example .env  # then edit it
make dev              # backend on :8000, frontend on :3000
```

`make dev` runs the API and the Vite dev server together. Vite proxies `/api` to
the backend, so the browser only ever talks to one origin and session cookies
work exactly as they do in production.

Other targets:

```bash
make test       # pytest with coverage
make lint       # ruff + mypy + tsc
make build      # production frontend build into frontend/dist
make check      # lint + test
make version    # print the current version
make help       # every target
```

## Configuration

All configuration is by environment variable, read only in
[`backend/wmf_scraper/settings.py`](backend/wmf_scraper/settings.py).

| Variable | Required | Description |
| --- | --- | --- |
| `ENVIRONMENT` | no | `production` (default) or `development`/`dev`/`local` |
| `DATABASE_PATH` | no | SQLite file path. Defaults to `data/wmf_scraper.db` |
| `STATIC_DIR` | no | Directory with the built frontend. Defaults to `static` |
| `SESSION_SECRET` | **in production** | Random string used to sign session cookies |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | at least one pair | Read-only web login |
| `SUPERADMIN_USERNAME` / `SUPERADMIN_PASSWORD` | at least one pair | Web login that can add and load competitions |
| `API_KEY` | no | Enables `Authorization: Bearer <key>` access for scripts, with the `superadmin` role |

In production the app refuses to start without `SESSION_SECRET` and at least one
credential pair.

## Authentication

The API lives under `/api`. `/api/version` and `/api/auth/*` are public;
everything else requires authentication:

* **Browser** — `POST /api/auth/login` with `{"username", "password"}` returns a
  signed, HttpOnly session cookie. Credentials are checked on the server, so the
  JavaScript bundle contains no secrets.
* **Scripts** — `Authorization: Bearer $API_KEY`, granted the `superadmin` role.

Endpoints that modify data (`/api/competition/add_*`, `/api/competition/remove_one`,
`/api/competitor/add_competitors_in_competition`, `/api/load/*`) additionally
require the `superadmin` role.

Interactive docs: `/api/docs`.

## Seeding

[`seed/`](seed/) holds ready-made request bodies for bulk operations:

```bash
BASE=https://wmf-scraper.fly.dev
curl -X POST "$BASE/api/competition/add_many"      -H "Authorization: Bearer $API_KEY" \
     -H 'Content-Type: application/json' -d @seed/competitions.json
curl -X POST "$BASE/api/load/load_many_competitions" -H "Authorization: Bearer $API_KEY" \
     -H 'Content-Type: application/json' -d @seed/load_competitions.json
```

## Versioning

`pyproject.toml` holds the one authoritative version number. Everything else
follows from it:

* `frontend/package.json` is kept in step by [`scripts/sync_version.py`](scripts/sync_version.py).
* The running app reports it at `/api/version`, read from the installed package
  metadata rather than from a hard-coded string or an environment variable.
* The UI shows it on the login card, in the navbar and on the About page — all
  three from `/api/version`, so what you read is what the server is running.

Never edit the version by hand:

```bash
make version        # 0.0.1
make bump-patch     # 0.0.1 -> 0.0.2   bug fixes
make bump-minor     # 0.0.2 -> 0.1.0   new functionality
make bump-major     # 0.1.0 -> 1.0.0   breaking changes
```

## Releasing

```bash
make bump-patch
git commit -am "Release v$(make -s version)"
make tag                       # creates v0.0.2 locally
git push origin master
git push origin v0.0.2         # this is what deploys
```

`make tag` refuses to run on a dirty tree, or when the version in
`pyproject.toml` has not been committed, so a tag always points at the commit
that actually carries that version.

Pushing the tag runs [`.github/workflows/release.yml`](.github/workflows/release.yml),
the only workflow in the repository. It:

1. checks the tag matches the version in `pyproject.toml` and `package.json`,
2. deploys to Fly, which builds the image from the `Dockerfile`,
3. polls `/api/version` until it reports the new version,
4. opens a GitHub release with generated notes.

It deliberately runs no tests — **run `make check` yourself before tagging.**

It needs exactly one repository secret:

| Secret | How to get it |
| --- | --- |
| `FLY_API_TOKEN` | `fly tokens create deploy -a wmf-scraper` |

Add it under *Settings → Secrets and variables → Actions → New repository secret*.
Nothing else is needed: the application secrets (`SESSION_SECRET`, the
credentials, `API_KEY`) live on Fly and are never read by CI.

## Deployment

The app deploys to the Fly.io app **`wmf-scraper`**, in `ams`, with the
`wmf_data` volume mounted at `/data` holding the SQLite database. Tag pushes
deploy automatically; `make deploy` deploys from your machine when you need to.

```bash
fly secrets set \
  SESSION_SECRET="$(openssl rand -hex 32)" \
  ADMIN_USERNAME=... ADMIN_PASSWORD=... \
  SUPERADMIN_USERNAME=... SUPERADMIN_PASSWORD=... \
  API_KEY=...
```

See [DEPLOY.md](DEPLOY.md) for the full procedure, including how the SQLite
database is preserved across deploys and how to back it up.
