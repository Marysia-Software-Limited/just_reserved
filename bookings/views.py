from datetime import datetime

from django.shortcuts import render
from django.views import View

from .models import Booking


def get_from_token(token: str):
    try:
        return Booking.get_qs().get(token=token)
    except Booking.DoesNotExist as _:
        return None


class BookingView(View):

    def action(self, booking):
        raise NotImplementedError()

    def get(self, request, token):
        booking = get_from_token(token)
        if booking is not None:
            self.action(booking)
        return render(request, "delete_booking.html")


class BookingActivateView(BookingView):
    def action(self, booking):
        booking.expired = booking.date_start
        booking.save()


class BookingDeleteView(BookingView):
    def action(self, booking):
        booking.expired = datetime.now()
        booking.save()
