# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-07-10

### Added

- `Client` with `activate`, `validate`, `heartbeat`, and `deactivate`
- Ed25519 envelope verification before lease parsing
- `LicenslySession` helper for background heartbeats
- Unit tests for signing fixtures
