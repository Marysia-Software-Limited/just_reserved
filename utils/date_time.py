from datetime import datetime, date
from typing import Union, TypeAlias

AnyDate: TypeAlias = Union[datetime, date]


def date_str(_date: AnyDate):
    return _date.strftime("%a, %d %b, %Y")


def time_str(_time: AnyDate):
    return _time.strftime("%H:%M")


def day(_date: AnyDate):
    return date(day=_date.day, month=_date.month, year=_date.year)


def equal_day(first_date: AnyDate, *dates: AnyDate) -> bool:
    first_date = day(first_date)
    for _date in dates:
        if day(_date) != first_date:
            return False
    return True


if __name__ == "__main__":
    print(equal_day(datetime.now(), date.today()))  # True
