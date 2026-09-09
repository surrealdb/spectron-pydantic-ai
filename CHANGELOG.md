# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-09-09

Renamed from `spectron-pydantic-ai` to `agent-memory-pydantic-ai`, and fixed the
SurrealDB SDK imports that `surrealdb.py`'s package split had already broken.

### Changed

- **BREAKING** Package renamed to `agent-memory-pydantic-ai`; the import root is
  now `agent_memory_pydantic_ai`.
- **BREAKING** Every `Spectron*` name loses the product prefix for `AgentMemory*`:
  `SpectronMemory` -> `AgentMemory`, `SpectronToolset` -> `AgentMemoryToolset`,
  `SpectronClient` -> `AgentMemoryClient`, `SpectronError` -> `AgentMemoryError`,
  `SpectronImportError` -> `AgentMemoryImportError`,
  `spectron_history_processor` -> `agent_memory_history_processor`.
- **BREAKING** Requires `surrealdb[memory]>=3.0.0b8`. The client moved out of the
  `surrealdb` wheel into its own `surrealdb-memory` distribution, so
  `surrealdb.spectron` no longer exists and `AsyncSpectron` is now `AsyncMemory`.

### Fixed

- Imports of `surrealdb.spectron`, which raised `ModuleNotFoundError` against any
  `surrealdb` release from 3.0.0b8 onward.

## [0.1.0] - 2026-07-16

Initial release. Targets the Spectron client bundled in `surrealdb >= 3.0.0a2`
(`surrealdb.AsyncSpectron`).

### Added

- `SpectronMemory`: a scoped async wrapper over the Spectron client with
  `connect(context, endpoint, api_key)`, `scoped`, and the memory verbs
  (`remember`, `remember_many`, `recall`, `query_context`, `reflect`, `forget`,
  `inspect`, and `upload` via the documents namespace). Its scope
  (`session_id`, `scope`, `on_behalf_of`) is applied as `scopes` on writes and
  `lens` on reads.
- `SpectronToolset`: a Pydantic AI toolset exposing memory operations as tools,
  with a configurable operation subset.
- `spectron_history_processor`: an auto-recall history processor with `recall`
  and `context` modes.
- `store_run` and `store_messages`: helpers that persist a run's messages back
  to Spectron via `remember_many`.
- `SpectronClient` protocol and `SpectronError` / `SpectronImportError`
  exceptions.
- Examples for the toolset, auto-recall, and a persistent multi-turn chat.

[Unreleased]: https://github.com/surrealdb/agent-memory-pydantic-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/surrealdb/agent-memory-pydantic-ai/releases/tag/v0.1.0
