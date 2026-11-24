# Feature: Host Overview Page

## What

NodeSense provides a lightweight browser page that summarizes the host's
operating system, kernel, model, uptime, machine time, CPU, memory, storage,
Docker containers and internet-test status.

## Why

Users need a glanceable operational view for a host without opening Home
Assistant or installing a separate dashboard. The page gives immediate context
when diagnosing load, capacity or container state.

## Acceptance Criteria

- [ ] The page is reachable on a configurable local port.
- [ ] It displays system identity and time information.
- [ ] It displays CPU, memory and storage totals alongside current usage.
- [ ] It displays container names and statuses when Docker visibility is
      available.
- [ ] It continues to serve a useful status response when optional Docker data
      is unavailable.

## Related

- [Project Intent](project-intent.md)
- [Decision: Lightweight Host Overview HTTP Surface](../decisions/007-web-overview-and-extended-telemetry.md)
- [Pattern: Polling JSON Overview](../knowledge/patterns/polling-json-overview.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Active (implemented in V2)
