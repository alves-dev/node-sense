# Decision: Atomic Local JSON Configuration

## Context

Each host needs independent editable cron and enablement settings that survive
container restarts without a database.

## Decision

Store the two editable values in `/data/config.json`, validate them on load and
write them through a temporary file followed by `os.replace` and `fsync`.

## Rationale

The configuration is small, local and naturally scoped to one agent. Atomic
replacement prevents a restart or interruption from leaving a partially written
JSON document.

## Alternatives Considered

Environment variables alone do not support runtime changes, and a database is
unnecessary for two values. Direct in-place JSON writes were not selected due to
partial-write risk.

## Outcomes

Persistence and restoration are covered by unit tests. Invalid persisted values
fall back to a valid default rather than preventing startup.

## Related

- [Feature: Resilient Agent Operation](../intent/feature-resilient-operation.md)
- [Pattern: Atomic JSON Persistence](../knowledge/patterns/atomic-json-persistence.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.
