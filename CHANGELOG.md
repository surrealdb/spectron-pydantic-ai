# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

Initial release.

### Added

- `SpectronMemory`: a scoped async wrapper over the Spectron client with
  `connect`, `scoped`, and the seven memory operations (`remember`, `recall`,
  `context`, `reflect`, `forget`, `upload`, `inspect`).
- `SpectronToolset`: a Pydantic AI toolset exposing memory operations as tools,
  with a configurable operation subset.
- `spectron_history_processor`: an auto-recall history processor with `recall`
  and `context` modes.
- `store_run` and `store_messages`: helpers that persist a run's messages back
  to Spectron.
- `SpectronClient` protocol and `SpectronError` / `SpectronImportError`
  exceptions.
- Examples for the toolset, auto-recall, and a persistent multi-turn chat.

[Unreleased]: https://github.com/surrealdb-dev/spectron-pydantic-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/surrealdb-dev/spectron-pydantic-ai/releases/tag/v0.1.0
