# Feature: Host Telemetry

## What

The agent presents the host name and an available CPU or SoC temperature as
Home Assistant entities. When a suitable temperature sensor is unavailable,
the temperature entity remains unavailable instead of showing a fabricated
zero value.

## Why

Users need a quick view of which host is reporting and whether its processor or
system-on-chip is operating at a reasonable temperature.

## Acceptance Criteria

- [ ] Each agent exposes one stable host identity entity.
- [ ] A suitable CPU/SoC temperature is shown when the host provides one.
- [ ] Ambient or unrelated sensors do not replace an available CPU/SoC sensor.
- [ ] Missing temperature data is represented as unavailable.

## Related

- [Project Intent](project-intent.md)
- [Decision: Telemetry Collection](../decisions/003-telemetry-collection.md)
- [Pattern: Ranked Sensor Selection](../knowledge/patterns/ranked-sensor-selection.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Active (already implemented)
