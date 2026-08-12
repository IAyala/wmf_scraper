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
├── pyproject.toml          Python project, managed with uv
├── Dockerfile              builds frontend + backend into one image
└── fly.toml                the single `wmf-scraper` app
```

## Requirements

* [uv](https://docs.astral.sh/uv/) for Python
* Node.js 20+ for the frontend
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

## Deployment

The app deploys to the Fly.io app **`wmf-scraper`**, in `ams`, with the
`wmf_data` volume mounted at `/data` holding the SQLite database.

```bash
fly secrets set \
  SESSION_SECRET="$(openssl rand -hex 32)" \
  ADMIN_USERNAME=... ADMIN_PASSWORD=... \
  SUPERADMIN_USERNAME=... SUPERADMIN_PASSWORD=... \
  API_KEY=...
fly deploy
```

See [DEPLOY.md](DEPLOY.md) for the full procedure, including how the database is
preserved across this refactor.
