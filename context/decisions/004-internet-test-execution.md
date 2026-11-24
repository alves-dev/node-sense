# Decision: Official Ookla CLI as a Bounded Async Subprocess

## Context

Internet measurements must be repeatable, use the official Ookla CLI, avoid
requiring host installation, and not allow concurrent bandwidth-heavy tests on
one host.

## Decision

Install the pinned official `speedtest` CLI in the Docker image, invoke it with
`asyncio.create_subprocess_exec` and explicit arguments, parse JSON output,
convert bandwidth to Mbit/s, enforce a timeout and protect execution with an
asyncio lock.

## Rationale

The image is self-contained, argument execution avoids shell injection, JSON is
more reliable than parsing human-readable output, and timeout/locking limits
resource impact.

## Alternatives Considered

Installing Ookla on the host, using an unpinned download, shell command strings,
or a Python speed-test library were not selected. The proposal also excludes
distributed locking between hosts in V1.

## Outcomes

The parser and bytes-per-second conversion are covered by unit tests. Builds
validate the CLI version. `arm/v7` remains intentionally unsupported until an
officially compatible package is validated.

## Related

- [Feature: Internet Speed Testing](../intent/feature-internet-speed-testing.md)
- [Pattern: Safe External Command Execution](../knowledge/patterns/safe-external-command.md)

## Status

- **Created**: 2026-11-24 (Phase: Intent)
- **Status**: Accepted
- **Note**: Documented from existing implementation.
