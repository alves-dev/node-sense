import json
from nodesense.collectors.speedtest import parse_speedtest
from nodesense.collectors.temperature import read_temperature
from nodesense.core.config import ConfigStore, Settings, validate_cron

def test_speedtest_bandwidth_is_mbit():
    result = parse_speedtest({"download": {"bandwidth": 12500000}, "upload": {"bandwidth": 2500000}, "ping": {"latency": 12.5, "jitter": 1.2}, "packetLoss": 0.5, "server": {"name": "Local", "id": 42}})
    assert result.download == 100.0; assert result.upload == 20.0; assert result.server_id == "42"

def test_invalid_and_too_frequent_cron():
    assert validate_cron("0 */4 * * *") == "0 */4 * * *"
    try: validate_cron("* * * * *")
    except ValueError: pass
    else: assert False

def test_config_persists_atomically(tmp_path):
    s = Settings("host", "Host", "mqtt", 1883, None, None, False, "nodesense", tmp_path, "UTC", None, 30, "speedtest", 10, 30, "0 */4 * * *", True)
    store = ConfigStore(s); store.load(); store.enabled = False; store.save()
    loaded = ConfigStore(s); loaded.load(); assert loaded.enabled is False; assert json.loads((tmp_path / "config.json").read_text())["enabled"] is False

def test_temperature_is_none_without_sensor(tmp_path):
    assert read_temperature(str(tmp_path)) == (None, None)

def test_temperature_prefers_cpu_package_over_ambient(tmp_path):
    thermal = tmp_path / "class/thermal/thermal_zone0"
    thermal.mkdir(parents=True); (thermal / "type").write_text("INT3400 Thermal"); (thermal / "temp").write_text("20000")
    hwmon = tmp_path / "class/hwmon/hwmon0"
    hwmon.mkdir(parents=True); (hwmon / "name").write_text("coretemp"); (hwmon / "temp1_label").write_text("Package id 0"); (hwmon / "temp1_input").write_text("52000")
    assert read_temperature(str(tmp_path)) == (52.0, str(hwmon / "temp1_input"))
