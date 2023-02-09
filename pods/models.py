from datetime import timedelta, time, datetime
from nptime import nptime

from django.db import models
from django.db.models import ForeignKey
from schedule.models import Rule


class Pod(models.Model):
    name = models.TextField(max_length=255)
    label = models.TextField(max_length=1024, blank=True)
    time_start = models.TimeField(default=time(hour=9))
    time_end = models.TimeField(default=time(hour=17))
    holidays = models.TextField(max_length=255, default="UK", null=True)
    rule = ForeignKey(
        Rule,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Default rule is a workdays only."
    )
    amount = models.IntegerField(default=1)

    def __str__(self):
        return self.label or self.name


class Service(models.Model):
    name = models.TextField(max_length=255)
    label = models.TextField(max_length=1024, blank=True)
    slot = models.DurationField(default=timedelta(minutes=30))

    def slots(self, pod: Pod):
        slot_time = nptime.from_time(pod.time_start)
        while slot_time < pod.time_end:
            yield slot_time
            slot_time += self.slot

    def __str__(self):
        return self.label or self.name
