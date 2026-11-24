# Pattern: Safe External Command Execution

## Description

Run an external measurement tool with an argument list, bounded time and
structured output parsing.

## When to Use

Use for tools that must run outside Python but receive fixed arguments and
return machine-readable output.

## Pattern

Use `asyncio.create_subprocess_exec`, never a shell string; capture stdout and
stderr; enforce a timeout; check the exit code; parse JSON only after success.

## Example

```python
process = await asyncio.create_subprocess_exec(
    command, "--accept-license", "--accept-gdpr", "--format=json",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
)
stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
if process.returncode != 0:
    raise RuntimeError("speedtest failed")
result = parse_speedtest(stdout)
```

## Files Using This Pattern

- `nodesense/collectors/speedtest.py` — runs and parses Ookla results.
- `nodesense/app.py` — serializes execution with an asyncio lock.

## Related

- [Decision: Official Ookla CLI as a Bounded Async Subprocess](../../decisions/004-internet-test-execution.md)
- [Feature: Internet Speed Testing](../../intent/feature-internet-speed-testing.md)

## Status

- **Created**: 2026-11-24
- **Status**: Active
