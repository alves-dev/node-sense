# Decision: V1 Scope and Deployment Constraints

## Context

The original implementation proposal defined a deliberately small per-host
agent: no central backend, database, custom frontend or detailed resource
monitoring in V1. It also required the Ookla CLI to be inside the image and
limited supported platforms to those that could be validated officially.

## Decision

Keep V1 focused on host identity, CPU/SoC temperature, internet speed testing,
Home Assistant controls and resilient local operation. Deploy one container per
Linux host with host networking, a read-only sysfs mount and a persistent `/data`
volume. Publish only validated `amd64` and `arm64` images; do not claim `arm/v7`
support. Treat cross-host coordination and missed-test replay as out of scope.

## Rationale

The focused scope keeps the agent lightweight and avoids introducing a backend
or database before the core telemetry workflow is proven. Host networking makes
the initial connectivity measurement representative while the read-only sysfs
mount and non-root process limit permissions. Explicit platform claims prevent
an unvalidated Ookla package from becoming an operational promise.

## Alternatives Considered

Adding CPU, RAM, disk, container and uptime collectors, creating a custom web
UI/API, adding distributed locking, or supporting `arm/v7` without an officially
validated compatible CLI were deferred. These remain possible future work, not
current V1 behavior.

## Outcomes

The implementation provides `compose.yaml`, `.env.example`, CI publication for
`linux/amd64` and `linux/arm64`, a local Mosquitto test path, and documented
limitations. The V2 host overview page is a deliberately small exception to
the original no-frontend V1 scope. Acceptance validation covers Docker
startup, MQTT discovery, temperature fallback, manual tests, persistence,
reconnect behavior, local mutual exclusion and the HTTP status surface.

## Related

- [Project Intent](../intent/project-intent.md)
- [Feature: Host Telemetry](../intent/feature-host-telemetry.md)
- [Feature: Internet Speed Testing](../intent/feature-internet-speed-testing.md)
- [Decision: Official Ookla CLI as a Bounded Async Subprocess](004-internet-test-execution.md)
- [Decision: Host Sensor Collection Without Privileged Mode](003-telemetry-collection.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Accepted
- **Note**: Consolidates the implemented scope and deployment constraints from
  the former implementation proposal.
