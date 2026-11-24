# Decision: Python 3.12 Minimal Agent Stack

## Context

NodeSense is a small Linux container agent with MQTT communication, cron
validation and subprocess-based measurements. It does not need a web server,
database or central API.

## Decision

Use Python 3.12+, `paho-mqtt` for MQTT, `croniter` for five-field cron
calculation, `asyncio` for the application loop and `pytest` for tests. Package
the application in a Python slim container.

## Rationale

The selected dependencies are small and directly map to the agent's needs.
Python's standard library supplies async process execution, JSON persistence,
signals, timezone handling and filesystem access without additional frameworks.

## Alternatives Considered

APScheduler, Pydantic, psutil, a web framework and a database were considered
in the original proposal but are not required by the implemented V1. The
existing code keeps the dependency surface smaller. Alternatives were not
otherwise documented in the codebase.

## Outcomes

The stack supports the current tests and container build. Dependency behavior
and upgrade outcomes should be recorded here as the project evolves.

## Related

- [Project Intent](../intent/project-intent.md)
- [Decision: Internet Test Execution](004-internet-test-execution.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.
