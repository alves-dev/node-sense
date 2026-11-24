import json

def discovery_payload(settings, mqtt):
    availability = {"topic": mqtt.topic("availability"), "payload_available": "online", "payload_not_available": "offline"}
    state, speed = mqtt.topic("system/state"), mqtt.topic("speedtest/state")
    system_keys = {"hostname", "temperature", "os", "kernel", "model", "uptime", "datetime", "cpu_cores", "cpu_usage", "memory_used", "memory_total", "memory_usage", "storage_used", "storage_total", "storage_usage", "containers"}
    device = {"identifiers": [f"nodesense_{settings.agent_id}"], "name": settings.agent_name, "manufacturer": "NodeSense", "model": "NodeSense Agent", "sw_version": "0.2.0"}
    base = {"availability": availability, "device": device}
    def sensor(key, name, template, **extra):
        return {**base, "platform": "sensor", "name": name, "unique_id": f"nodesense_{settings.agent_id}_{key}", "state_topic": state if key in system_keys else speed, "value_template": template, **extra}
    components = {
        "hostname": sensor("hostname", "NodeSense — Host", "{{ value_json.hostname }}", icon="mdi:server", entity_category="diagnostic"),
        "temperature": sensor("temperature", "CPU/SoC — Temperature", "{{ value_json.temperature if value_json.temperature is defined else none }}", icon="mdi:thermometer", device_class="temperature", unit_of_measurement="°C", state_class="measurement"),
        "os": sensor("os", "System — Operating System", "{{ value_json.os if value_json.os is defined else none }}", icon="mdi:linux", entity_category="diagnostic"),
        "kernel": sensor("kernel", "System — Linux Kernel", "{{ value_json.kernel if value_json.kernel is defined else none }}", icon="mdi:console-line", entity_category="diagnostic"),
        "model": sensor("model", "System — Model", "{{ value_json.model if value_json.model is defined else none }}", icon="mdi:computer", entity_category="diagnostic"),
        "uptime": sensor("uptime", "System — Uptime", "{{ value_json.uptime_seconds if value_json.uptime_seconds is defined else none }}", icon="mdi:timer-outline", device_class="duration", unit_of_measurement="s", state_class="measurement"),
        "datetime": sensor("datetime", "System — Machine Time", "{{ value_json.datetime if value_json.datetime is defined else none }}", icon="mdi:clock-outline", device_class="timestamp", entity_category="diagnostic"),
        "cpu_cores": sensor("cpu_cores", "System — CPU Cores", "{{ value_json.cpu_cores if value_json.cpu_cores is defined else none }}", icon="mdi:cpu-64-bit", entity_category="diagnostic"),
        "cpu_usage": sensor("cpu_usage", "System — CPU Usage", "{{ value_json.cpu_usage_pct if value_json.cpu_usage_pct is defined else none }}", icon="mdi:cpu-64-bit", unit_of_measurement="%", state_class="measurement"),
        "memory_used": sensor("memory_used", "System — Memory Used", "{{ value_json.memory_used_bytes if value_json.memory_used_bytes is defined else none }}", icon="mdi:memory", device_class="data_size", unit_of_measurement="B", state_class="measurement"),
        "memory_total": sensor("memory_total", "System — Memory Total", "{{ value_json.memory_total_bytes if value_json.memory_total_bytes is defined else none }}", icon="mdi:memory", device_class="data_size", unit_of_measurement="B", entity_category="diagnostic"),
        "memory_usage": sensor("memory_usage", "System — Memory Usage", "{{ value_json.memory_used_pct if value_json.memory_used_pct is defined else none }}", icon="mdi:memory", unit_of_measurement="%", state_class="measurement"),
        "storage_used": sensor("storage_used", "System — Storage Used", "{{ value_json.storage_used_bytes if value_json.storage_used_bytes is defined else none }}", icon="mdi:harddisk", device_class="data_size", unit_of_measurement="B", state_class="measurement"),
        "storage_total": sensor("storage_total", "System — Storage Total", "{{ value_json.storage_total_bytes if value_json.storage_total_bytes is defined else none }}", icon="mdi:harddisk", device_class="data_size", unit_of_measurement="B", entity_category="diagnostic"),
        "storage_usage": sensor("storage_usage", "System — Storage Usage", "{{ value_json.storage_used_pct if value_json.storage_used_pct is defined else none }}", icon="mdi:harddisk", unit_of_measurement="%", state_class="measurement"),
        "containers": sensor("containers", "System — Containers", "{{ value_json.container_count if value_json.container_count is defined else none }}", icon="mdi:docker", state_class="measurement", entity_category="diagnostic"),
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
    return {"device": device, "origin": {"name": "NodeSense", "sw": "0.2.0"}, "components": components}

def publish_discovery(settings, mqtt):
    mqtt.client.publish(f"homeassistant/device/nodesense_{settings.agent_id}/config", json.dumps(discovery_payload(settings, mqtt), separators=(",", ":")), qos=1, retain=True)
