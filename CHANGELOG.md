# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [Unreleased]

## [0.2.2] - 2026-09-17

### Fixed
- README tree diagram and dashes were mojibake after the repo rename.
- `BasePage.open()` retries once when Chrome shows its transient "This page couldn't load" error page, which was making random UI tests time out.

## [0.2.1] - 2026-09-17

### Changed
- Bumped `pytest` 9.0.3 → 9.1.1 and `requests` 2.33.1 → 2.34.2.
- Bumped `actions/checkout`, `actions/setup-python` and `actions/upload-artifact` to v7.

## [0.2.0] - 2026-09-17

### Added
- CODEOWNERS, so PRs auto-request review from the maintainer.

### Fixed
- CI no longer runs twice per PR: `push` trigger limited to `main`.
- `BookingClient.list_bookings()` tolerates both response shapes the demo site returns for `GET /booking`.

## [0.1.0] - 2026-09-17

### Added
- `BookingClient` wrapping the restful-booker booking API (create/get/update/delete, admin login).
- Page objects for the home page, reservation flow and admin Report calendar.
- API tests: CRUD, invalid payloads, unknown id; booking creation parametrized over three rooms.
- UI tests: home → reservation form → confirmation, blank-name validation.
- Integration tests: API-created booking visible in admin UI, API-deleted booking gone from UI,
  UI-created booking readable via API.
- Screenshot on UI test failure; self-contained pytest-html report.
- GitHub Actions: `api` job then `ui` job, on push/PR/nightly, reports uploaded as artifacts.
- Dependabot for pip and GitHub Actions; pinned requirements.
- MIT license, code of conduct, issue and PR templates.

[Unreleased]: https://github.com/LSaiko/double-booked/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/LSaiko/double-booked/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/LSaiko/double-booked/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/LSaiko/double-booked/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/LSaiko/double-booked/releases/tag/v0.1.0
