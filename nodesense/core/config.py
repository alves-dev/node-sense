from __future__ import annotations
import json, os, re, socket, tempfile
from dataclasses import dataclass
from pathlib import Path
from croniter import croniter

def validate_cron(expression: str, minimum_minutes: int = 30) -> str:
    from datetime import datetime, timedelta
    value = " ".join(expression.split())
    if len(value.split()) != 5 or not croniter.is_valid(value):
        raise ValueError("cron deve conter cinco campos válidos")
    iterator = croniter(value, datetime.now())
    first = iterator.get_next(datetime)
    second = iterator.get_next(datetime)
    if (second - first) < timedelta(minutes=minimum_minutes):
        raise ValueError(f"cron deve respeitar intervalo mínimo de {minimum_minutes} minutos")
    return value

def safe_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip()).strip("_")
    return value or "node"

@dataclass(frozen=True)
class Settings:
    agent_id: str; agent_name: str; mqtt_host: str; mqtt_port: int
    mqtt_username: str | None; mqtt_password: str | None; mqtt_tls: bool
    mqtt_base_topic: str; data_dir: Path; timezone: str; sensor_path: str | None
    temperature_interval: int; speedtest_command: str; speedtest_timeout: int
    minimum_cron_minutes: int; default_cron: str; enabled: bool

    @classmethod
    def from_env(cls) -> "Settings":
        name = os.getenv("AGENT_NAME") or socket.gethostname()
        return cls(safe_id(os.getenv("AGENT_ID") or name), name, os.getenv("MQTT_HOST", "localhost"), int(os.getenv("MQTT_PORT", "1883")), os.getenv("MQTT_USERNAME") or None, os.getenv("MQTT_PASSWORD") or None, os.getenv("MQTT_TLS", "false").lower() in {"1", "true", "yes"}, os.getenv("MQTT_BASE_TOPIC", "nodesense").strip("/") or "nodesense", Path(os.getenv("DATA_DIR", "/data")), os.getenv("TZ", "America/Sao_Paulo"), os.getenv("SENSOR_PATH") or None, int(os.getenv("TEMPERATURE_INTERVAL", "30")), os.getenv("SPEEDTEST_COMMAND", "speedtest"), int(os.getenv("SPEEDTEST_TIMEOUT", "180")), int(os.getenv("MINIMUM_CRON_MINUTES", "30")), os.getenv("SPEEDTEST_CRON", "0 */4 * * *"), os.getenv("SPEEDTEST_ENABLED", "true").lower() not in {"0", "false", "off"})

class ConfigStore:
    def __init__(self, settings: Settings):
        self.path = settings.data_dir / "config.json"; self.settings = settings
        self.cron = settings.default_cron; self.enabled = settings.enabled
    def load(self):
        try:
            data = json.loads(self.path.read_text())
            self.cron = validate_cron(str(data.get("cron", self.cron)), self.settings.minimum_cron_minutes)
            self.enabled = bool(data.get("enabled", self.enabled))
        except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError):
            self.cron = validate_cron(self.cron, self.settings.minimum_cron_minutes)
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix="config.", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump({"cron": self.cron, "enabled": self.enabled}, stream, indent=2); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
