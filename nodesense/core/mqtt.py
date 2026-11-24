from __future__ import annotations
import json, logging
import paho.mqtt.client as mqtt
LOG = logging.getLogger(__name__)

class MQTT:
    def __init__(self, settings, on_message):
        self.settings = settings; self.on_message = on_message; self.on_connect = None
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"nodesense-{settings.agent_id}")
        if settings.mqtt_username: self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        if settings.mqtt_tls: self.client.tls_set()
        self.client.will_set(self.topic("availability"), "offline", qos=1, retain=True)
        self.client.on_connect = self._connected
        self.client.on_message = lambda _c, _u, m: self.on_message(m.topic, m.payload.decode(errors="replace"))
    def topic(self, suffix): return f"{self.settings.mqtt_base_topic}/{self.settings.agent_id}/{suffix}"
    def connect(self):
        self.client.reconnect_delay_set(1, 60); self.client.connect_async(self.settings.mqtt_host, self.settings.mqtt_port, 60); self.client.loop_start()
    def _connected(self, _client, _userdata, _flags, _reason, _properties=None):
        LOG.info("mqtt conectado host=%s", self.settings.mqtt_host)
        self.client.publish(self.topic("availability"), "online", qos=1, retain=True)
        self.client.subscribe([(self.topic("speedtest/cron/set"), 1), (self.topic("speedtest/enabled/set"), 1), (self.topic("speedtest/run/set"), 1)])
        if self.on_connect:
            self.on_connect()
    def publish(self, suffix, payload, *, retain=False, qos=1):
        if isinstance(payload, (dict, list)): payload = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        self.client.publish(self.topic(suffix), payload, qos=qos, retain=retain)
    def close(self):
        try:
            self.client.publish(self.topic("availability"), "offline", qos=1, retain=True); self.client.disconnect(); self.client.loop_stop()
        except Exception: LOG.exception("erro ao encerrar mqtt")
