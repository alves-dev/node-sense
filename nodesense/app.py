from __future__ import annotations
import asyncio, logging, os, signal
from datetime import datetime, timezone
from .collectors.speedtest import run_speedtest
from .collectors.temperature import read_temperature
from .collectors.system import DockerCollector, SystemCollector
from .core.config import ConfigStore, Settings, validate_cron
from .core.discovery import publish_discovery
from .core.mqtt import MQTT
from .core.scheduler import next_run
from .web import WebServer
LOG = logging.getLogger("nodesense")

class Agent:
    def __init__(self, settings):
        self.settings, self.store = settings, ConfigStore(settings); self.store.load(); self.loop = asyncio.get_running_loop(); self.mqtt = MQTT(settings, self._mqtt_message); self.mqtt.on_connect = self.on_mqtt_connect; self.system = SystemCollector(settings); self.docker = DockerCollector(settings.docker_socket); self.web = WebServer(settings, self.web_state); self.current_system = {"hostname": settings.agent_name}; self.containers = []; self.running = False; self.last = {"status": "idle"}; self.lock = asyncio.Lock(); self.next_scheduled = None
    def web_state(self):
        return {**self.current_system, "containers": self.containers or [], "container_count": len(self.containers) if self.containers is not None else None, "speedtest": {**self.last, "next_test": self.scheduled_time()}}
    def on_mqtt_connect(self):
        publish_discovery(self.settings, self.mqtt); self.publish_speed(); self.publish_config()
    def _mqtt_message(self, topic, payload): self.loop.call_soon_threadsafe(lambda: asyncio.create_task(self.command(topic, payload)))
    async def command(self, topic, payload):
        if topic.endswith("cron/set"):
            try: self.store.cron = validate_cron(payload, self.settings.minimum_cron_minutes); self.next_scheduled = None; self.store.save(); self.publish_config()
            except ValueError as exc: LOG.warning("cron rejeitado: %s", exc); self.mqtt.publish("speedtest/status", {"status": "error", "last_error": str(exc)}, retain=False); self.publish_config()
        elif topic.endswith("enabled/set") and payload.upper() in {"ON", "OFF"}:
            self.store.enabled = payload.upper() == "ON"; self.next_scheduled = None; self.store.save(); self.publish_config()
        elif topic.endswith("run/set") and payload.upper() in {"PRESS", "RUN", "1"}: await self.run_test("manual")
    def scheduled_time(self):
        return next_run(self.store.cron, self.settings.timezone).isoformat()
    def publish_config(self):
        self.mqtt.publish("speedtest/cron/state", self.store.cron, retain=True); self.mqtt.publish("speedtest/enabled/state", "ON" if self.store.enabled else "OFF", retain=True); self.mqtt.publish("speedtest/next_run", self.scheduled_time(), retain=True)
    def publish_speed(self):
        payload = {**self.last, "next_test": self.scheduled_time()}
        self.mqtt.publish("speedtest/state", payload, retain=True)
    async def run_test(self, reason):
        if self.lock.locked(): LOG.warning("teste ignorado: execução já em andamento (%s)", reason); return
        async with self.lock:
            self.last = {"status": "running"}; self.publish_speed()
            try:
                result = await run_speedtest(self.settings.speedtest_command, self.settings.speedtest_timeout)
                self.last = {"status": "success", "download": result.download, "upload": result.upload, "ping": result.ping, "jitter": result.jitter, "packet_loss": result.packet_loss, "server": result.server or result.server_id, "last_test": datetime.now(timezone.utc).isoformat()}
            except Exception as exc: LOG.warning("teste falhou: %s", exc); self.last = {"status": "error", "last_error": str(exc)}
            self.publish_speed(); self.publish_config()
    async def tick(self):
        temperature, sensor = read_temperature("/host/sys" if os.path.exists("/host/sys") else "/sys", self.settings.sensor_path)
        self.current_system = {**self.system.collect(), "temperature": temperature, "temperature_sensor": sensor}
        self.containers = self.docker.collect()
        self.current_system["containers"] = self.containers or []
        self.current_system["container_count"] = len(self.containers) if self.containers is not None else None
        if self.current_system.get("storage"):
            self.current_system.update({f"storage_{key}": value for key, value in self.current_system["storage"].items()})
        mqtt_system = {key: value for key, value in self.current_system.items() if key != "containers"}
        self.mqtt.publish("system/state", mqtt_system, retain=True)
        if self.store.enabled:
            current = next_run(self.store.cron, self.settings.timezone) if self.next_scheduled is None else self.next_scheduled
            if datetime.now(current.tzinfo) >= current:
                self.next_scheduled = None
                await self.run_test("cron")
            else:
                self.next_scheduled = current
                self.mqtt.publish("speedtest/next_run", current.isoformat(), retain=True)
    async def start(self):
        self.web.start()
        self.mqtt.connect()
        while self.running:
            await self.tick(); await asyncio.sleep(max(5, self.settings.temperature_interval))
    async def shutdown(self): self.running = False; self.web.close(); self.mqtt.close()

def run():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    async def runner():
        agent = Agent(Settings.from_env()); agent.running = True; loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM): loop.add_signal_handler(sig, lambda: asyncio.create_task(agent.shutdown()))
        try: await agent.start()
        finally: await agent.shutdown()
    asyncio.run(runner())
