from __future__ import annotations
import asyncio, json
from dataclasses import dataclass

@dataclass
class SpeedTestResult:
    download: float | None = None; upload: float | None = None; ping: float | None = None; jitter: float | None = None; packet_loss: float | None = None; server: str | None = None; server_id: str | None = None

def parse_speedtest(payload: str | bytes | dict) -> SpeedTestResult:
    data = json.loads(payload) if isinstance(payload, (str, bytes)) else payload
    if not isinstance(data, dict): raise ValueError("resultado Ookla não é um objeto JSON")
    d, u, p, s = data.get("download") or {}, data.get("upload") or {}, data.get("ping") or {}, data.get("server") or {}
    return SpeedTestResult((float(d["bandwidth"]) * 8 / 1_000_000) if d.get("bandwidth") is not None else None, (float(u["bandwidth"]) * 8 / 1_000_000) if u.get("bandwidth") is not None else None, float(p["latency"]) if p.get("latency") is not None else None, float(p["jitter"]) if p.get("jitter") is not None else None, float(data["packetLoss"]) if data.get("packetLoss") is not None else None, s.get("name"), str(s["id"]) if s.get("id") is not None else None)

async def run_speedtest(command="speedtest", timeout=180):
    process = await asyncio.create_subprocess_exec(command, "--accept-license", "--accept-gdpr", "--format=json", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try: stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill(); await process.wait(); raise TimeoutError(f"speedtest excedeu {timeout}s")
    if process.returncode != 0: raise RuntimeError(f"speedtest falhou ({process.returncode}): {stderr.decode(errors='replace').strip()[-500:]}")
    return parse_speedtest(stdout)
