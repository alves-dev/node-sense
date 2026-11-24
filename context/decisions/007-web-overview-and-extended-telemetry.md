# Decision: Lightweight Host Overview HTTP Surface

## Context

The original V1 intentionally had no frontend, but a small Glances-like view
is useful for local diagnosis. The same collected data should feed the page and
Home Assistant without adding a backend or a JavaScript build system.

## Decision

Expose a standard-library HTTP server on fixed internal port `9130`, serving a
static HTML page, the NodeSense logo asset and a JSON `/api/state` endpoint.
Collect OS/kernel, model, uptime, machine time, CPU, memory, storage and Docker
container data in the agent and publish the relevant values through the
existing retained `system/state` MQTT payload.

Mount host sysfs at `/host/sys`, host root at `/host/root` and the Docker socket
at `/var/run/docker.sock`, all read-only. Require only the host Docker socket
group ID through `DOCKER_GID` so the application can remain non-root; the paths
are image conventions rather than user-facing settings.

## Rationale

The standard library keeps the image small and avoids a second service. A
single state collector prevents the web page and HA from disagreeing because
they read different sources. Polling JSON is sufficient for a glanceable page
and avoids websockets or a persistent frontend build.

## Alternatives Considered

A separate frontend framework, REST framework, websocket server, privileged
container or Docker CLI subprocess were not selected for V2. A broad host-root
mount is a deliberate operational tradeoff for accurate storage reporting and
must remain read-only and documented.

## Outcomes

The page and `/api/state` were smoke-tested in a container. Host OS, model,
kernel, uptime, CPU, memory and storage were observed successfully. Docker
container listing works when the supplied supplemental group matches the socket
GID; otherwise the UI reports container data as unavailable rather than zero.

## Related

- [Feature: Host Overview Page](../intent/feature-host-overview.md)
- [Feature: Host Telemetry](../intent/feature-host-telemetry.md)
- [Pattern: Polling JSON Overview](../knowledge/patterns/polling-json-overview.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Accepted
- **Note**: Records the V2 extension of the existing agent.
