# Pattern: Polling JSON Overview

## Description

Serve a static page that periodically fetches a local JSON state endpoint and
renders the latest values without a frontend build pipeline.

## When to Use

Use for a small operational dashboard where a few-second refresh is adequate and
the agent already owns the state being displayed.

## Pattern

Keep the HTML/CSS/JavaScript self-contained, expose `/api/state` with
`Cache-Control: no-store`, render optional values as unavailable, and use the
same collector state for MQTT and HTTP consumers.

## Example

```javascript
async function refresh() {
  const state = await (await fetch('/api/state', {cache: 'no-store'})).json();
  document.getElementById('cpu').textContent = `${state.cpu_usage_pct}%`;
}
refresh();
setInterval(refresh, 5000);
```

## Files Using This Pattern

- `nodesense/web.py` — serves the page and JSON endpoint.
- `nodesense/app.py` — supplies the shared state callback.
- `nodesense/collectors/system.py` — produces the overview state.

## Related

- [Decision: Lightweight Host Overview HTTP Surface](../../decisions/007-web-overview-and-extended-telemetry.md)
- [Feature: Host Overview Page](../../intent/feature-host-overview.md)

## Status

- **Created**: 2026-11-24
- **Status**: Active
