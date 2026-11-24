# Pattern: Ranked Sensor Selection

## Description

Choose the most semantically appropriate available host sensor instead of
assuming that the first kernel path is the desired measurement.

## When to Use

Use when Linux exposes multiple thermal zones or hardware-monitoring inputs and
their names identify different physical sources.

## Pattern

Collect candidates, assign scores from names/labels, sort by score, validate
the numeric range, and return the first valid reading. Permit an explicit path
override.

## Example

```python
if name == "coretemp" and "package" in label:
    score = 100
elif kind == "x86_pkg_temp":
    score = 90
for score, path in sorted(candidates, key=lambda item: (-item[0], str(item[1]))):
    value = _read(path)
    if score > 0 and value is not None:
        return value, str(path)
```

## Files Using This Pattern

- `nodesense/collectors/temperature.py` — ranks CPU/SoC temperature sources.
- `tests/test_core.py` — verifies package temperature wins over ambient data.

## Related

- [Decision: Host Sensor Collection Without Privileged Mode](../../decisions/003-telemetry-collection.md)
- [Feature: Host Telemetry](../../intent/feature-host-telemetry.md)

## Status

- **Created**: 2026-11-24
- **Status**: Active
