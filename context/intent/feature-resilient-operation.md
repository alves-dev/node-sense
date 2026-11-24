# Feature: Resilient Agent Operation

## What

The agent keeps its editable settings across restarts, reports availability,
reconnects to MQTT when the broker is temporarily unavailable, and continues
its local schedule without requiring Home Assistant to remain online.

## Why

Monitoring should remain useful during normal homelab interruptions and should
not lose per-host configuration when a container or broker restarts.

## Acceptance Criteria

- [ ] Schedule and enablement survive an agent restart.
- [ ] MQTT availability changes to offline when the agent is disconnected and
      returns online after reconnection.
- [ ] Discovery and current state are restored after MQTT reconnection.
- [ ] Shutdown closes the agent gracefully.
- [ ] Old MQTT commands are not replayed after reconnecting.

## Related

- [Project Intent](project-intent.md)
- [Decision: MQTT and Home Assistant Integration](../decisions/002-mqtt-home-assistant.md)
- [Decision: Persistent Configuration](../decisions/005-persistent-configuration.md)
- [Pattern: Atomic JSON Persistence](../knowledge/patterns/atomic-json-persistence.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Active (already implemented)
