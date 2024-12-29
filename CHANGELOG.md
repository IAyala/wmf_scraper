# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Unreleased]
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

[Unreleased]: https://github.com/IAyala/wmf_scraper/compare/v1.1.0...master
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
