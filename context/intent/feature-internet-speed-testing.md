# Feature: Internet Speed Testing

## What

NodeSense periodically or manually measures the host's internet connection and
exposes the latest download, upload, latency, jitter, packet loss, server,
status and test timestamps in Home Assistant.

## Why

Homelab operators need to notice degraded connectivity and compare the current
network experience with historical Home Assistant data without installing a
separate monitoring dashboard on each host.

## Acceptance Criteria

- [ ] A user can run a test manually.
- [ ] A user can configure a recurring schedule with a minimum safe frequency.
- [ ] Successful tests expose measured values with correct units.
- [ ] Failed tests expose an error state without replacing previous metrics with
      artificial zero values.
- [ ] A second test cannot start while another test is running on the same host.

## Related

- [Project Intent](project-intent.md)
- [Decision: Internet Test Execution](../decisions/004-internet-test-execution.md)
- [Pattern: Safe External Command Execution](../knowledge/patterns/safe-external-command.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Active (already implemented)
