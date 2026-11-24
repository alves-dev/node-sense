# Changelog

## [Current State] - Context Mesh Added

### Existing Features Documented

- Host identity and CPU/SoC temperature telemetry.
- Internet speed testing with manual and scheduled execution.
- Home Assistant MQTT Discovery and controls.
- Persistent configuration, availability and reconnect behavior.
- Docker deployment and GHCR multi-architecture publication.
- Host overview page and extended system/container telemetry.

### Tech Stack Documented

- Python 3.12+.
- `paho-mqtt`, `croniter`, `asyncio` and JSON persistence.
- Official Ookla Speedtest CLI in the Docker image.
- Docker Compose, Buildx/QEMU and GitHub Actions.

### Patterns Identified

- Device-based MQTT Discovery.
- Atomic JSON persistence.
- Safe bounded external command execution.
- Ranked thermal sensor selection.
- Polling JSON overview page.

### Configuration Simplification

- Fixed internal paths for web, persistence, host sysfs, host root and Docker
  socket mounts.
- Kept `DOCKER_GID` as the only host-specific mount permission value needed for
  container listing.
- Fixed the Speedtest timeout at 180 seconds instead of exposing another
  deployment variable.

### Proposal Reconciliation

- The former `nodesense-proposta-implementacao.md` was reconciled into the
  intent, feature and decision files above.
- V1 scope, deployment constraints, validated architecture claims and deferred
  capabilities are recorded in
  [Decision: V1 Scope and Deployment Constraints](../decisions/006-v1-scope-and-deployment.md).

---

*Context Mesh added: 2026-11-24*
*This changelog documents the state when Context Mesh was added.*
*Future changes will be tracked below.*
