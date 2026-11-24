# Changelog

## 0.1.0 - 2026-11-24

### Added

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
