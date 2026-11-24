from pathlib import Path


def _read(path: Path):
    try:
        raw = float(path.read_text().strip())
        value = raw / 1000 if abs(raw) > 200 else raw
        return round(value, 1) if -40 <= value <= 150 else None
    except (OSError, ValueError):
        return None


def read_temperature(base: str = "/sys", preferred: str | None = None):
    """Return the most representative CPU/SoC temperature available.

    ACPI/ambient zones such as INT3400 and wireless-device zones are deliberately
    ranked below CPU package sensors. This avoids reporting the common 20 °C
    ambient value when coretemp/x86_pkg_temp is available.
    """
    if preferred:
        path = Path(preferred)
        value = _read(path)
        if value is not None:
            return value, str(path)

    root = Path(base)
    candidates: list[tuple[int, Path]] = []
    hwmon = root / "class/hwmon"
    for directory in sorted(hwmon.glob("hwmon*")):
        try:
            name = (directory / "name").read_text().strip().lower()
        except OSError:
            name = ""
        for input_path in sorted(directory.glob("temp*_input")):
            label_path = input_path.with_name(input_path.name.replace("_input", "_label"))
            try:
                label = label_path.read_text().strip().lower()
            except OSError:
                label = ""
            score = 40
            if name == "coretemp":
                score = 75
                if "package" in label:
                    score = 100
            elif name in {"k10temp", "zenpower"}:
                score = 95
            candidates.append((score, input_path))

    thermal = root / "class/thermal"
    for directory in sorted(thermal.glob("thermal_zone*")):
        try:
            kind = (directory / "type").read_text().strip().lower()
        except OSError:
            kind = ""
        score = 10
        if kind in {"x86_pkg_temp", "cpu-thermal", "cpu_thermal"}:
            score = 90
        elif "cpu" in kind or "soc" in kind or kind == "tcpu":
            score = 80
        elif kind in {"int3400 thermal", "iwlwifi_1"} or kind.startswith("sns"):
            score = 0
        candidates.append((score, directory / "temp"))

    for score, path in sorted(candidates, key=lambda item: (-item[0], str(item[1]))):
        if score <= 0:
            continue
        value = _read(path)
        if value is not None:
            return value, str(path)
    return None, None
