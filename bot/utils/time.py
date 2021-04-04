import typing as t
from datetime import datetime

from dateutil.relativedelta import relativedelta


def humanize_time(time_delta: relativedelta, min_unit: str = "seconds") -> str:
    """Convert a relative delta into human readable time."""
    time_dict = {
        "years": time_delta.years,
        "months": time_delta.months,
        "weeks": time_delta.weeks,
        "days": time_delta.days,
        "hours": time_delta.hours,
        "minutes": time_delta.minutes,
        "seconds": time_delta.seconds,
        "microseconds": time_delta.microseconds,
    }

    time_list = []

    for unit, value in time_dict.items():
        if value:
            time_list.append(f"{value} {unit if value != 1 else unit[:-1]}")

        if unit == min_unit:
            break

    if len(time_list) > 1:
        time_str = " ".join(time_list[:-1])
        time_str += f" and {time_list[-1]}"
    elif len(time_list) == 0:
        time_str = "now"
    else:
        time_str = time_list[0]

    return time_str


def time_ago(
    _from: datetime, to: t.Optional[datetime] = None, min_unit: str = "seconds"
) -> str:
    if not to:
        to = datetime.utcnow()

    time_delta = relativedelta(to, _from)
    return f"{humanize_time(time_delta, min_unit=min_unit)} ago."
