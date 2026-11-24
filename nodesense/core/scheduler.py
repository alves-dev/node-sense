from datetime import datetime
from zoneinfo import ZoneInfo
from croniter import croniter

def next_run(expression: str, timezone: str) -> datetime:
    now = datetime.now(ZoneInfo(timezone)); return croniter(expression, now).get_next(datetime)
