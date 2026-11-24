# Home Assistant entities

NodeSense creates one MQTT device per agent through Home Assistant MQTT Discovery.
The device identifier is `nodesense_<agent_id>` and all entities use stable
`unique_id` values based on the agent ID.

## Entities

| Entity | HA platform | Name | Unit / class | Icon | Source |
|---|---|---|---|---|---|
| `hostname` | Sensor | NodeSense — Host | Diagnostic | `mdi:server` | `system/state` |
| `temperature` | Sensor | CPU/SoC — Temperature | °C, temperature | `mdi:thermometer` | `system/state` |
| `os` | Sensor | System — Operating System | Diagnostic | `mdi:linux` | `system/state` |
| `kernel` | Sensor | System — Linux Kernel | Diagnostic | `mdi:console-line` | `system/state` |
| `model` | Sensor | System — Model | Diagnostic | `mdi:computer` | `system/state` |
| `uptime` | Sensor | System — Uptime | s, duration | `mdi:timer-outline` | `system/state` |
| `datetime` | Sensor | System — Machine Time | Timestamp | `mdi:clock-outline` | `system/state` |
| `cpu_cores` | Sensor | System — CPU Cores | Diagnostic | `mdi:cpu-64-bit` | `system/state` |
| `cpu_usage` | Sensor | System — CPU Usage | %, measurement | `mdi:cpu-64-bit` | `system/state` |
| `memory_used` | Sensor | System — Memory Used | B, data size | `mdi:memory` | `system/state` |
| `memory_total` | Sensor | System — Memory Total | B, data size | `mdi:memory` | `system/state` |
| `memory_usage` | Sensor | System — Memory Usage | %, measurement | `mdi:memory` | `system/state` |
| `storage_used` | Sensor | System — Storage Used | B, data size | `mdi:harddisk` | `system/state` |
| `storage_total` | Sensor | System — Storage Total | B, data size | `mdi:harddisk` | `system/state` |
| `storage_usage` | Sensor | System — Storage Usage | %, measurement | `mdi:harddisk` | `system/state` |
| `containers` | Sensor | System — Containers | Count | `mdi:docker` | `system/state` |
| `download` | Sensor | Internet — Download | Mbit/s, 0 decimals | `mdi:download-network` | `speedtest/state` |
| `upload` | Sensor | Internet — Upload | Mbit/s, 0 decimals | `mdi:upload-network` | `speedtest/state` |
| `ping` | Sensor | Internet — Ping | ms, 1 decimal | `mdi:speedometer` | `speedtest/state` |
| `jitter` | Sensor | Internet — Jitter | ms | `mdi:waveform` | `speedtest/state` |
| `packet_loss` | Sensor | Internet — Packet Loss | % | `mdi:percent` | `speedtest/state` |
| `server` | Sensor | Internet — Server | Diagnostic | `mdi:server-network` | `speedtest/state` |
| `last_test` | Sensor | Internet — Last Test | Timestamp | `mdi:calendar-check` | `speedtest/state` |
| `next_test` | Sensor | Internet — Next Test | Timestamp | `mdi:calendar-clock` | `speedtest/state` |
| `status` | Sensor | Internet — Test Status | Diagnostic | `mdi:information-outline` | `speedtest/state` |
| `cron` | Text | Internet — Schedule | Five-field cron | `mdi:calendar-edit` | `speedtest/cron/state` |
| `enabled` | Switch | Internet — Tests Enabled | `ON` / `OFF` | `mdi:toggle-switch` | `speedtest/enabled/state` |
| `run` | Button | Internet — Run Test | Manual trigger | `mdi:play-circle` | Command only |

## MQTT topics

For an agent with ID `server1` and base topic `nodesense`:

```text
nodesense/server1/availability
nodesense/server1/system/state
nodesense/server1/speedtest/state
nodesense/server1/speedtest/status
nodesense/server1/speedtest/cron/state
nodesense/server1/speedtest/cron/set
nodesense/server1/speedtest/enabled/state
nodesense/server1/speedtest/enabled/set
nodesense/server1/speedtest/run/set
nodesense/server1/speedtest/next_run
```

The Discovery configuration is retained at:

```text
homeassistant/device/nodesense_server1/config
```

Commands are intentionally not retained, so reconnecting MQTT cannot repeat a
manual test or apply an old configuration command.

## State payloads

`system/state` contains the host identity and the selected temperature sensor:

```json
{
  "hostname": "server1",
  "temperature": 52.0,
  "temperature_sensor": "/host/sys/class/hwmon/hwmon5/temp1_input"
  ,"uptime_seconds": 285432.3,
  "datetime": "2026-11-24T16:05:24-03:00",
  "cpu_usage_pct": 8.3,
  "memory_total_bytes": 16430813184,
  "memory_used_bytes": 12383244288,
  "memory_used_pct": 75.1,
  "storage_total_bytes": 267015901184,
  "storage_used_bytes": 197789466624,
  "storage_used_pct": 74.1,
  "container_count": 8
}
```

`speedtest/state` contains the latest result and the next scheduled execution:

```json
{
  "status": "success",
  "download": 312.0,
  "upload": 98.0,
  "ping": 12.4,
  "jitter": 1.1,
  "packet_loss": 0.0,
  "server": "Example ISP",
  "last_test": "2026-11-24T12:00:00+00:00",
  "next_test": "2026-11-24T16:00:00-03:00"
}
```

Fields that are unavailable are omitted or rendered unavailable by Home
Assistant. NodeSense does not replace missing temperature or failed test
metrics with zero values.

## Temperature selection

The collector prefers CPU/SoC sensors in this order of relevance:

1. Explicitly configured `SENSOR_PATH`.
2. `coretemp` package temperature (`Package id 0`).
3. `k10temp` or `zenpower` package temperature.
4. `x86_pkg_temp` or CPU/SoC thermal zones.
5. Other valid hardware-monitoring inputs as a fallback.

Ambient ACPI zones such as `INT3400 Thermal` and unrelated device zones such as
Wi-Fi are excluded when a better CPU/SoC sensor is available.
