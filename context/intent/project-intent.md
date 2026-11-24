# Project Intent: NodeSense

## What

NodeSense is a lightweight host-telemetry agent for Linux homelab hosts. It
reports host identity, CPU/SoC temperature and internet speed-test results to
Home Assistant, where users can observe status, history and controls.

## Why

Homelab operators need a small per-host agent that exposes useful operational
telemetry without a central backend, database or custom dashboard. NodeSense
consolidates basic host and connectivity visibility in the Home Assistant
interface already used to operate the homelab.

## Current State

The project is an active V2 implementation. It runs as a Docker container,
communicates through MQTT Discovery, persists editable schedule settings, and
publishes multi-architecture images for Linux amd64 and arm64 through GHCR.

## Current Features

- Host identity and CPU/SoC temperature reporting.
- Internet speed-test results and status reporting.
- Home Assistant controls for scheduling, enabling and manually running tests.
- Stable MQTT availability and discovery for one device per host.
- Persistent configuration and local protection against concurrent tests.
- Docker deployment and CI publication for amd64 and arm64.
- Local host overview page for quick operational inspection.

## Related

- [Feature: Host Telemetry](feature-host-telemetry.md)
- [Feature: Internet Speed Testing](feature-internet-speed-testing.md)
- [Feature: Home Assistant Controls](feature-home-assistant-controls.md)
- [Feature: Resilient Agent Operation](feature-resilient-operation.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Active
- **Note**: Generated from the existing NodeSense codebase and documentation.
