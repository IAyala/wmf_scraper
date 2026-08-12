# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Unreleased]
------------

[3.0.1] - 2026-08-12
------------

### Fixed
- Competitions whose competitor list has not been published yet can now be
  loaded. WatchMeFly only publishes the standings table and the pilot list once
  an event has official results, so an in-progress event such as the 2026
  French Nationals exposed task results with no roster to match them against.
  The roster is now rebuilt from the task results in that case.
- A result whose competitor cannot be resolved is skipped and reported in
  `LoadCompetitionResponse.result_no_competitor` instead of being stored
  against a `-1` placeholder id. Because `(task_id, competitor_id)` is the
  primary key, two such rows in one task raised a UNIQUE constraint error,
  and a single one was silently attributed to a competitor that does not exist.

### Changed
- Task pages are fetched with a thread pool instead of a process pool. The work
  is HTTP-bound, and forking a pool out of the async server process is fragile
  now that Python 3.14 defaults to the forkserver start method.

[3.0.0] - 2026-08-12
------------

Merged the `wmf_scraper` and `wmf_scraper_front` repositories into one
fullstack project deployed as a single Fly app.

### Added
- FastAPI serves the compiled React frontend from the same origin as the API.
- Server-side session authentication: `POST /api/auth/login` issues a signed,
  HttpOnly cookie. `/api/auth/logout` and `/api/auth/me` complete the flow.
- `SESSION_SECRET`, `ADMIN_*` and `SUPERADMIN_*` environment variables, checked
  at startup in production.
- `Makefile`, `.env.example` and a GitHub Actions workflow.

### Changed
- **Breaking:** all API endpoints moved under `/api` (`/version` is now
  `/api/version`). OpenAPI docs are at `/api/docs`.
- **Breaking:** every endpoint except `/api/version` and `/api/auth/*` now
  requires authentication. Previously the GET endpoints were public and the
  login screen was cosmetic. `Authorization: Bearer $API_KEY` still works for
  scripts and is granted the `superadmin` role.
- Packaging moved from Poetry to uv; the backend is now the importable
  `wmf_scraper` package with absolute imports, and the `parser` module was
  renamed to `parsers` so it no longer shadows a standard library name.
- Frontend build moved from Create React App to Vite. React 18 and the
  components are unchanged.
- Frontend requests are relative to `/api`, so no CORS middleware and no
  `REACT_APP_*` build arguments.
- Single root `Dockerfile` and `fly.toml`.

### Fixed
- The frontend no longer embeds the API key or the admin and superadmin
  passwords in the JavaScript bundle, where anyone could read them.
- `ssl._create_default_https_context` is no longer globally replaced with the
  unverified context; the scraper now verifies WatchMeFly's certificate against
  certifi's CA bundle.

### Removed
- The separate `wmf-scraper-front` Fly app, its Dockerfile, nginx config and
  deploy script.
- Committed build output, coverage reports and coverage badges.
- bump2version configuration; the version lives only in `pyproject.toml` and is
  read at runtime from the package metadata.
- Per-repo `environment/` dev-image scripts and `scripts/` bash helpers,
  replaced by the `Makefile`.
- FontAwesome, which was imported but never used, along with `sqlalchemy_utils`,
  `fastapi-utils`, `typing-inspect` and the unused timing helpers.

[2.1.3] - 2025-11-28
------------

[2.1.2] - 2025-11-28
------------

[2.1.1] - 2025-11-28
------------

[2.1.0] - 2025-11-28
------------

[2.0.0] - 2025-11-28
------------

[1.1.2] - 2024-12-29
------------

[1.1.1] - 2024-12-29
------------

[1.1.0] - 2024-12-29
------------

[1.0.0] - 2023-10-15
------------
Bumping major version, this is a fully functional version compliant with version 1.0.0 of the frontend

[0.2.2] - 2023-10-08
------------
More robust way to select which test must run, just in case files are not ordered similarly between different filesystems

[0.2.1] - 2023-10-06
------------
Use new image version properly

[0.2.0] - 2023-10-06
------------
Code is ready to function with a preliminary version of the frontend

[0.1.2] - 2023-10-05
------------
CORS issue resolved. A couple of new endpoints added

[0.1.1] - 2023-09-27
------------
We are now able to load task results in parallel after a big refactoring. It takes 40 seconds to load 16 competitions

[0.1.0] - 2023-09-20
------------
Now a complete loading workflow is in place. Ready to build more functionality from this basic feature

[0.0.6] - 2023-09-18
------------
Small refactoring. Now it is possible to load a competition, but competitor loading is still pending

[0.0.5] - 2023-09-16
------------
Endpoints created to retrieve:
- Tasks from a competition
- Competitors from a competition

Added some tests that parse a static HTML example files and assess results are as expected

[0.0.4] - 2023-09-14
------------
Some endpoints created:
- One to get current version tag
- One to add a competition
- One to get competion with a certain description

Coverage 100% still :joy:

[0.0.3] - 2023-09-06
------------
Removed some files that must not exist in the repo

[0.0.2] - 2023-09-06
------------
Minor bugs fixed. Tests added. Coverage 100%. Ready to go

[0.0.1] - 2023-09-06
------------
First version, with the skeleton of the project ready to go

[Unreleased]: https://github.com/IAyala/wmf_scraper/compare/v3.0.1...master
[3.0.1]: https://github.com/IAyala/wmf_scraper/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/IAyala/wmf_scraper/compare/v2.1.3...v3.0.0
[2.1.3]: https://github.com/IAyala/wmf_scraper/compare/v2.1.2...v2.1.3
[2.1.2]: https://github.com/IAyala/wmf_scraper/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/IAyala/wmf_scraper/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/IAyala/wmf_scraper/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/IAyala/wmf_scraper/compare/v1.1.2...v2.0.0
[1.1.2]: https://github.com/IAyala/wmf_scraper/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/IAyala/wmf_scraper/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/IAyala/wmf_scraper/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/IAyala/wmf_scraper/compare/v0.2.2...v1.0.0
[0.2.2]: https://github.com/IAyala/wmf_scraper/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/IAyala/wmf_scraper/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/IAyala/wmf_scraper/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/IAyala/wmf_scraper/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/IAyala/wmf_scraper/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/IAyala/wmf_scraper/compare/v0.0.6...v0.1.0
[0.0.6]: https://github.com/IAyala/wmf_scraper/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/IAyala/wmf_scraper/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/IAyala/wmf_scraper/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/IAyala/wmf_scraper/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/IAyala/wmf_scraper/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/IAyala/wmf_scraper/compare/v0.0.0...v0.0.1
