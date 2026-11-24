# Pattern: Device-Based MQTT Discovery

## Description

Publish one retained Home Assistant device-discovery document containing all
entities for an agent, with stable IDs derived from the agent ID.

## When to Use

Use when one process owns multiple related MQTT entities and they should appear
as one device in Home Assistant.

## Pattern

Keep the availability topic shared, use separate state topics for system and
speed-test data, and never retain command topics. Republish Discovery and
current state after every MQTT connection.

## Example

```python
device = {
    "identifiers": [f"nodesense_{settings.agent_id}"],
    "name": settings.agent_name,
    "manufacturer": "NodeSense",
    "model": "NodeSense Agent",
}
payload = {"device": device, "components": components}
mqtt.client.publish(discovery_topic, json.dumps(payload), qos=1, retain=True)
```

## Files Using This Pattern

- `nodesense/core/discovery.py` — builds and publishes the device payload.
- `nodesense/core/mqtt.py` — publishes availability and subscribes to commands.
- `nodesense/app.py` — republishes discovery on connection.

## Related

- [Decision: MQTT Device-Based Home Assistant Integration](../../decisions/002-mqtt-home-assistant.md)
- [Feature: Home Assistant Controls](../../intent/feature-home-assistant-controls.md)

## Status

- **Created**: 2026-11-24
- **Status**: Active
