# Pattern: Atomic JSON Persistence

## Description

Persist a small local configuration by writing a complete temporary file,
flushing it, and replacing the target atomically.

## When to Use

Use for small state/configuration documents where a database is unnecessary but
partial writes must not corrupt the next startup.

## Pattern

Create the temporary file in the same directory, write and `fsync` it, call
`os.replace`, and remove a leftover temporary file in `finally`.

## Example

```python
fd, temporary = tempfile.mkstemp(dir=self.path.parent)
try:
    with os.fdopen(fd, "w") as stream:
        json.dump(payload, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, self.path)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)
```

## Files Using This Pattern

- `nodesense/core/config.py` — persists cron and enablement settings.

## Related

- [Decision: Atomic Local JSON Configuration](../../decisions/005-persistent-configuration.md)
- [Feature: Resilient Agent Operation](../../intent/feature-resilient-operation.md)

## Status

- **Created**: 2026-11-24
- **Status**: Active
