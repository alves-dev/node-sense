# Changelog

## 0.3.0 - 2026-11-25

### Changed

- Machine time is published as text in the format `YYYY-MM-DD HH:MM:SS ±HH:MM`.
- Memory and storage entities use GB by default; uptime uses days.
- The system model entity uses `mdi:desktop-tower-monitor`.

## 0.2.0 - 2026-11-24

### Added

- Local host overview page and JSON status endpoint.
- Extended system, storage and Docker container telemetry.
- Per-container Docker memory usage in the local web dashboard, displayed in MB.
- NodeSense favicon for the web page.

### Changed

- Setuptools package discovery is restricted to the `nodesense` package so the
  CI editable install does not treat documentation and static assets as Python
  packages.
- Internal container paths and the web port are fixed conventions; only the
  Docker socket GID needs host-specific configuration for container listing.
- Speedtest timeout is fixed at 180 seconds and is no longer exposed as a
  deployment variable.
- Per-container memory details are kept local to the web dashboard and are not
  published to Home Assistant.
- Compose now uses the default Docker network and publishes web port `9130`;
  MQTT connectivity is configured through `MQTT_HOST`.

## 0.1.0 - 2026-11-24

### Added

- Optional host overview web page on port 9130 with a JSON status endpoint.
- System telemetry for OS/kernel, model, uptime, machine time, CPU, memory,
  storage and Docker containers.
- GitHub Actions workflow for publishing multi-architecture images to GHCR.
- NodeSense agent with MQTT availability, reconnect and Home Assistant MQTT Discovery.
- Stable host identity and a single device per agent.
- CPU/SoC temperature collection with preference for CPU package sensors.
- Official Ookla Speedtest CLI included in the Docker image.
- Internet test sensors for download, upload, ping, jitter, packet loss, server and timestamps.
- Home Assistant controls for schedule, enable/disable and manual test execution.
- Atomic persistent configuration in `/data/config.json`.
- Local execution lock and timeout protection for speed tests.
- Docker Compose setup, local Mosquitto configuration and CI workflow.
- Unit tests for parsing, units, cron validation, persistence and temperature selection.

### Changed

- Internet entities use explicit English names and dedicated icons.
- Ping display precision is one decimal place; download and upload use zero decimals.
- Packet Loss uses the valid `mdi:percent` icon.
- `next_test` is included in the retained speed-test state payload.

### Limitations

- `arm/v7` is not declared supported until an officially compatible Ookla package is validated.
