# Feature: Home Assistant Controls

## What

The agent creates one Home Assistant device per host with discoverable entities
for internet-test status, schedule, enablement and manual execution.

## Why

Users should be able to observe and control each host from the Home Assistant
interface they already use, without a separate NodeSense web application.

## Acceptance Criteria

- [ ] All entities for one host belong to one identifiable device.
- [ ] Entity names clearly distinguish internet-test metrics from host metrics.
- [ ] The schedule can be edited and its valid value is reflected back.
- [ ] Tests can be enabled or disabled independently for each host.
- [ ] A manual run control is available.

## Related

- [Project Intent](project-intent.md)
- [Decision: MQTT and Home Assistant Integration](../decisions/002-mqtt-home-assistant.md)
- [Pattern: Device-Based MQTT Discovery](../knowledge/patterns/device-mqtt-discovery.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Active (already implemented)
