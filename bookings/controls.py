from datetime import datetime
from typing import Optional

import flet as ft
from flet_django import *
from nptime import nptime

from django.utils.translation import gettext as _

from pods.models import Pod
from .forms import BookingEmailForm
from .models import Booking, EXPIRE_MINUTES


class BookingFormView(object):

    def __init__(self, calendar_date, time: nptime, duration, pod):
        calendar_date = datetime(day=calendar_date.day, month=calendar_date.month, year=calendar_date.year)
        date_start = calendar_date + time.to_timedelta()
        date_end = date_start + duration

        self.date_start: datetime = date_start
        self.date_end: datetime = date_end
        self.pod: Pod = pod

        self.email_input: ft.TextField = ft.TextField(
            keyboard_type=ft.KeyboardType.EMAIL,
            label=_("Email"),
            helper_text=_("Enter the email address to save your reservation.")
        )
        self.email_errors = ft.Markdown()
        self.message: ft.Control = ft.Text()
        self.__form_dialog: Optional[ft.AlertDialog] = None
        self.__page: Optional[ft.Page] = None
        self.title: ft.Control = ft.Text(_("Enter your email for booking"))
        self.buttons: ft.Row = ft.Row()

    @property
    def bookings(self):
        return Booking.bookings(self.pod, self.date_start, self.date_end)

    def get_form_view(self, page) -> ft.View:

        self.buttons.controls = [
            ft.TextButton(_("Reject"), on_click=lambda _: self.close()),
            ft.TextButton(_("Reserve"), on_click=lambda _: self.submit()),
        ]
        column = ft.Column(
            controls=[
                self.title,
                self.email_input,
                self.email_errors,
                self.message,
                self.buttons
            ]
        )
        controls = [ft.Container(
            content=column
        )]

        return ft_view(
            page,
            controls=controls,
        )

    def submit(self):
        data = {
            "email": self.email_input.value
        }
        form = BookingEmailForm(data)
        if form.is_valid():
            self.email_errors.value = ""
            booking = Booking(
                pod=self.pod,
                date_start=self.date_start,
                date_end=self.date_end,
                email=form.cleaned_data["email"]
            )

            bookings = self.bookings.filter(email=booking.email)
            if bookings.count():
                on_replace = self.on_replace(booking)
                return self.alert_dialog(on_replace, bookings)
            else:
                self.save(booking)
        else:
            email_html_error = form.errors.get("email")

            if email_html_error:
                self.email_errors.value = email_html_error.as_text()
                self.update()

    def alert_dialog(self, on_replace, bookings):

        messages = [_("What too much is not healthy.")]
        word: str = _("You already have")
        for booking in bookings:
            messages.append(
                _("{word} the execution reserved for {term}.").format(word=word, term=booking.term_str))
            word = _("You have also")

        messages.append(
            _("Do you want to cancel this date and book a new one?"))

        self.title.value = _("Decide man!")
        self.message.value = " ".join(messages)
        self.buttons.controls = [
            ft.TextButton(_("Reject"), on_click=self.on_reset),
            ft.TextButton(_("Replace"), on_click=on_replace),
        ]

        self.update()

    def save(self, booking):
        if booking.count < 1:
            return self.message_dialog(
                message=_("The term already reserved, try another!"),
                title=_("Term is unavailable")
            )
        booking.save()
        # self.close()
        message = _("""You reserved {pod} on the term {term}.
        Confirm please within {expire} minutes by clicking on the link that you will find in an email sent to 
         address {email}.
        """).format(pod=self.pod, expire=EXPIRE_MINUTES, term=booking.term_str, email=booking.email)
        self.message_dialog(
            message=message,
            title=_("We saved the reservation. We are waiting for confirmation.")
        )

    def message_dialog(
            self,
            message: str,
            title: str = "",
            button_text: str = _("OK"),
            on_click=None
    ):

        on_click = on_click or self.on_reset

        self.title.value = title
        self.message.value = message
        self.buttons.controls = [
            ft.TextButton(button_text, on_click=on_click),
        ]
        self.update()

    def __call__(self, page: GenericPage):
        self.page = page
        return self.get_form_view(page)

    def close(self):
        if self.page:
            if self.page.dialog:
                self.page.dialog.open = False
            self.page.ft_page.views.pop()
            self.update()

    def update(self, *controls):
        self.page.update(*controls)

    def on_replace(self, booking: Booking):
        def __on_replace(*_):
            """TODO: use transaction here"""
            self.bookings.filter(email=booking.email).delete()
            self.save(booking)

        return __on_replace

    def on_reset(self, *_):
        self.close()
