import json

def discovery_payload(settings, mqtt):
    availability = {"topic": mqtt.topic("availability"), "payload_available": "online", "payload_not_available": "offline"}
    state, speed = mqtt.topic("system/state"), mqtt.topic("speedtest/state")
    device = {"identifiers": [f"nodesense_{settings.agent_id}"], "name": settings.agent_name, "manufacturer": "NodeSense", "model": "NodeSense Agent", "sw_version": "0.1.0"}
    base = {"availability": availability, "device": device}
    def sensor(key, name, template, **extra):
        return {**base, "platform": "sensor", "name": name, "unique_id": f"nodesense_{settings.agent_id}_{key}", "state_topic": state if key in {"hostname", "temperature"} else speed, "value_template": template, **extra}
    components = {
        "hostname": sensor("hostname", "NodeSense — Host", "{{ value_json.hostname }}", icon="mdi:server", entity_category="diagnostic"),
        "temperature": sensor("temperature", "CPU/SoC — Temperature", "{{ value_json.temperature if value_json.temperature is defined else none }}", icon="mdi:thermometer", device_class="temperature", unit_of_measurement="°C", state_class="measurement"),
        "download": sensor("download", "Internet — Download", "{{ value_json.download if value_json.download is defined else none }}", icon="mdi:download-network", suggested_display_precision=0, unit_of_measurement="Mbit/s", state_class="measurement"),
        "upload": sensor("upload", "Internet — Upload", "{{ value_json.upload if value_json.upload is defined else none }}", icon="mdi:upload-network", suggested_display_precision=0, unit_of_measurement="Mbit/s", state_class="measurement"),
        "ping": sensor("ping", "Internet — Ping", "{{ value_json.ping if value_json.ping is defined else none }}", icon="mdi:speedometer", suggested_display_precision=1, unit_of_measurement="ms", state_class="measurement"),
        "jitter": sensor("jitter", "Internet — Jitter", "{{ value_json.jitter if value_json.jitter is defined else none }}", icon="mdi:waveform", unit_of_measurement="ms", state_class="measurement"),
        "packet_loss": sensor("packet_loss", "Internet — Packet Loss", "{{ value_json.packet_loss if value_json.packet_loss is defined else none }}", icon="mdi:percent", unit_of_measurement="%", state_class="measurement"),
        "server": sensor("server", "Internet — Server", "{{ value_json.server if value_json.server is defined else none }}", icon="mdi:server-network", entity_category="diagnostic"),
        "last_test": sensor("last_test", "Internet — Last Test", "{{ value_json.last_test if value_json.last_test is defined else none }}", icon="mdi:calendar-check", device_class="timestamp", entity_category="diagnostic"),
        "next_test": sensor("next_test", "Internet — Next Test", "{{ value_json.next_test if value_json.next_test is defined else none }}", icon="mdi:calendar-clock", device_class="timestamp", entity_category="diagnostic"),
        "status": sensor("status", "Internet — Test Status", "{{ value_json.status }}", icon="mdi:information-outline", entity_category="diagnostic"),
        "cron": {**base, "name": "Internet — Schedule", "icon": "mdi:calendar-edit", "unique_id": f"nodesense_{settings.agent_id}_cron", "platform": "text", "state_topic": mqtt.topic("speedtest/cron/state"), "command_topic": mqtt.topic("speedtest/cron/set"), "min": 1, "max": 100},
        "enabled": {**base, "name": "Internet — Tests Enabled", "icon": "mdi:toggle-switch", "unique_id": f"nodesense_{settings.agent_id}_enabled", "platform": "switch", "state_topic": mqtt.topic("speedtest/enabled/state"), "command_topic": mqtt.topic("speedtest/enabled/set"), "payload_on": "ON", "payload_off": "OFF", "state_on": "ON", "state_off": "OFF"},
        "run": {**base, "name": "Internet — Run Test", "icon": "mdi:play-circle", "unique_id": f"nodesense_{settings.agent_id}_run", "platform": "button", "command_topic": mqtt.topic("speedtest/run/set"), "payload_press": "PRESS"},
    }
    return {"device": device, "origin": {"name": "NodeSense", "sw": "0.1.0"}, "components": components}

def publish_discovery(settings, mqtt):
    mqtt.client.publish(f"homeassistant/device/nodesense_{settings.agent_id}/config", json.dumps(discovery_payload(settings, mqtt), separators=(",", ":")), qos=1, retain=True)
