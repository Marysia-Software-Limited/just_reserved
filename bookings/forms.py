from datetime import datetime

from django.db.models import Q
from nptime import nptime

from django import forms

from .models import Booking


class BookingEmailForm(forms.Form):
    email = forms.EmailField(required=True)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"

    def __init__(self, calendar_date, time: nptime, duration, pod, initial=None, *args, **kwargs):
        initial = initial or {}

        calendar_date = datetime(day=calendar_date.day, month=calendar_date.month, year=calendar_date.year)
        date_start = calendar_date + time.to_timedelta()
        date_end = date_start + duration

        self.date_start = date_start
        self.date_end = date_end
        self.pod = pod

        super().__init__(initial=initial, *args, **kwargs)

    @property
    def conflicts(self):
        return Booking.objects \
            .filter(pod=self.pod) \
            .filter(
            Q(date_start__lt=self.date_end, date_start__gte=self.date_start) |
            Q(date_end__lte=self.date_start, date_end__gt=self.date_end)
        )

    @property
    def amount(self):
        return self.pod.amount - self.conflicts.count()
