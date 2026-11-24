# Decision: Host Sensor Collection Without Privileged Mode

## Context

Temperature data differs between Linux hosts and not every thermal zone means
CPU temperature. The container must read host sensors without requiring
`privileged: true`.

## Decision

Read read-only host sysfs paths, rank CPU/SoC sensor candidates, prefer package
temperature sources such as `coretemp/Package id 0`, and return unavailable
when no valid reading exists.

## Rationale

Ranking avoids selecting common ambient ACPI or unrelated device values such as
the 20 °C `INT3400 Thermal` zone. A read-only `/sys` mount reduces permissions
while keeping the deployment simple.

## Alternatives Considered

Using the first thermal zone, using only one hard-coded path, invoking external
sensor utilities, or requiring privileged mode were not selected. They are less
portable or grant more access than necessary.

## Outcomes

The collector correctly selected the CPU package temperature on the validation
host and added a test that rejects the ambient-zone-first behavior.

## Related

- [Feature: Host Telemetry](../intent/feature-host-telemetry.md)
- [Pattern: Ranked Sensor Selection](../knowledge/patterns/ranked-sensor-selection.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.
