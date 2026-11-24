# Decision: MQTT Device-Based Home Assistant Integration

## Context

NodeSense must expose one stable device per host, survive broker interruptions,
and avoid a custom API or frontend. Home Assistant already supports MQTT
Discovery, availability and command/state topics.

## Decision

Use MQTT as the sole integration boundary. Publish a retained device-based
Discovery document, retained state/configuration topics, a retained online/offline
availability topic with Last Will, and non-retained command topics.

## Rationale

This keeps the agent stateless from Home Assistant's perspective, makes entity
creation idempotent, supports reconnects, and avoids replaying old commands. A
stable explicit agent ID prevents container IDs from changing entity identity.

## Alternatives Considered

A REST API, a custom Home Assistant integration and a central backend are
explicitly outside the V1 scope. Entity-by-entity discovery was not selected;
device-based discovery groups the host entities under one device.

## Outcomes

The implementation publishes `homeassistant/device/nodesense_<agent_id>/config`
and stable per-entity unique IDs. MQTT smoke tests confirmed discovery and state
publication with Mosquitto.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Home Assistant Controls](../intent/feature-home-assistant-controls.md)
- [Feature: Resilient Agent Operation](../intent/feature-resilient-operation.md)
- [Pattern: Device-Based MQTT Discovery](../knowledge/patterns/device-mqtt-discovery.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.
