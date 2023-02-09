from datetime import datetime

from django.db import models
from django.db.models import Q
from nptime import nptime

from pods.models import Pod


class Booking(models.Model):
    pod = models.ForeignKey(Pod, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()

    @classmethod
    def get_slot(cls, calendar_date, time: nptime, duration, pod):
        calendar_date = datetime(day=calendar_date.day, month=calendar_date.month, year=calendar_date.year)
        date_start = calendar_date + time.to_timedelta()
        date_end = date_start + duration
        return cls(pod=pod, date_start=date_start, date_end=date_end)

    @property
    def conflicts(self):
        return Booking.objects \
            .filter(pod=self.pod) \
            .filter(
            Q(date_start__lt=self.date_end, date_start__gte=self.date_start) |
            Q(date_end__lte=self.date_start, date_end__gt=self.date_end))

    @property
    def count(self):
        return self.pod.amount - self.conflicts.count()

    def __str__(self):
        return ",".join(
            map(str, (
                self.pod,
                self.date_start,
                self.date_end
            ))
        )
