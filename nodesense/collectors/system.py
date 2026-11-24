from __future__ import annotations

import json
import os
import platform
import socket
import shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text().strip() or None
    except OSError:
        return None


def _os_release(path: str) -> str:
    values = {}
    try:
        lines = Path(path).read_text().splitlines()
    except OSError:
        lines = []
    for line in lines:
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
    return values.get("PRETTY_NAME") or values.get("NAME") or platform.system()


def _cpu_times() -> tuple[int, int] | None:
    try:
        fields = _read_text(Path("/proc/stat")).splitlines()[0].split()[1:]
        values = [int(value) for value in fields]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        return sum(values), idle
    except (AttributeError, IndexError, ValueError, OSError):
        return None


class SystemCollector:
    def __init__(self, settings):
        self.settings = settings
        self.previous_cpu = _cpu_times()

    def _cpu_usage(self) -> float | None:
        current = _cpu_times()
        if not current or not self.previous_cpu:
            self.previous_cpu = current
            return None
        total_delta = current[0] - self.previous_cpu[0]
        idle_delta = current[1] - self.previous_cpu[1]
        self.previous_cpu = current
        return round(max(0.0, min(100.0, (1 - idle_delta / total_delta) * 100)), 1) if total_delta else None

    def _model(self) -> str:
        base = Path("/host/sys") if Path("/host/sys").exists() else Path("/sys")
        for relative in ("devices/virtual/dmi/id/product_name", "firmware/devicetree/base/model"):
            value = _read_text(base / relative)
            if value:
                return value
        return platform.machine()

    def collect(self) -> dict:
        memory = {}
        for line in _read_text(Path("/proc/meminfo")).splitlines() if _read_text(Path("/proc/meminfo")) else []:
            key, _, value = line.partition(":")
            if key in {"MemTotal", "MemAvailable"}:
                memory[key] = int(value.strip().split()[0]) * 1024
        total_memory = memory.get("MemTotal")
        available_memory = memory.get("MemAvailable")
        used_memory = total_memory - available_memory if total_memory is not None and available_memory is not None else None
        storage = None
        try:
            usage = shutil.disk_usage(self.settings.storage_path)
            storage = {"total_bytes": usage.total, "used_bytes": usage.used, "free_bytes": usage.free, "used_pct": round(usage.used / usage.total * 100, 1) if usage.total else None}
        except OSError:
            pass
        uptime = None
        try:
            uptime = round(float(Path("/proc/uptime").read_text().split()[0]), 1)
        except (OSError, ValueError, IndexError):
            pass
        return {
            "hostname": self.settings.agent_name or socket.gethostname(),
            "os": _os_release(self.settings.host_os_release),
            "kernel": platform.release(),
            "model": self._model(),
            "uptime_seconds": uptime,
            "datetime": datetime.now(ZoneInfo(self.settings.timezone)).isoformat(),
            "cpu_cores": os.cpu_count(),
            "cpu_usage_pct": self._cpu_usage(),
            "memory_total_bytes": total_memory,
            "memory_used_bytes": used_memory,
            "memory_used_pct": round(used_memory / total_memory * 100, 1) if used_memory is not None and total_memory else None,
            "storage": storage,
        }


class DockerCollector:
    def __init__(self, socket_path: str):
        self.socket_path = socket_path

    def collect(self) -> list[dict] | None:
        if not Path(self.socket_path).exists():
            return None
        try:
            import socket as socket_module
            client = socket_module.socket(socket_module.AF_UNIX, socket_module.SOCK_STREAM)
            client.settimeout(2)
            client.connect(self.socket_path)
            client.sendall(b"GET /containers/json?all=true HTTP/1.0\r\nHost: docker\r\n\r\n")
            response = b""
            while chunk := client.recv(65536):
                response += chunk
            client.close()
            body = response.split(b"\r\n\r\n", 1)[1]
            containers = json.loads(body)
            return [{"name": (item.get("Names") or [item.get("Id", "unknown")])[0].lstrip("/"), "status": item.get("Status", item.get("State", "unknown")), "state": item.get("State", "unknown")} for item in containers]
        except (OSError, ValueError, IndexError, json.JSONDecodeError):
            return None
