from datetime import datetime, date, time
from typing import Union


def date_str(_date: Union[datetime, date]):
    return _date.strftime("%a, %d %b, %Y")


def time_str(_time: Union[datetime, time]):
    return _time.strftime("%H:%M")
