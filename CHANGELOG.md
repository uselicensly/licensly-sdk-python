# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Vendor signing fixtures under `tests/fixtures/`; remove `scripts/fetch-contract.sh`
- Align `validate` and `activate` with Client API contract 0.4.1
- Parse unsigned sessionless validation results without signature verification
- Map `app_version_too_old` and `plan_limit` API errors

## [0.1.0] — 2026-07-10

### Added

- `Client` with `activate`, `validate`, `heartbeat`, and `deactivate`
- Ed25519 envelope verification before lease parsing
- `LicenslySession` helper for background heartbeats
- Unit tests for signing fixtures
