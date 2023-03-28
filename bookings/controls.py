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
            helper_text=_("Enter your email address."),
            color=ft.colors.BLACK,
            content_padding=20
        )
        self.email_errors = ft.Markdown()
        self.message: ft.Control = ft.Text()
        self.__form_dialog: Optional[ft.AlertDialog] = None
        self.__page: Optional[ft.Page] = None
        self.title: ft.Control = ft.Container(
            ft.Text(
                _("Of course, it is just a dummy application - you won't reserve anything. There are different reasons to write down your email address. First of all - we want to keep you updated with our growing technology (it's changing fast, but we won't spam your mailbox), second - we want to be sure if you decide to build your app, you will have our contact just under your hand, and - last but not least - we will give you 25% off for your first application build with us. We respect your privacy, you can resign from receiving our newsletter anytime."),
                color=ft.colors.BLACK,
                text_align=ft.TextAlign.CENTER,
                size=18,
                weight=ft.FontWeight.BOLD
            ),
            padding=20,
            margin=20,
            alignment=ft.alignment.center
        )
        self.buttons: ft.Row = ft.Row()

    @property
    def bookings(self):
        return Booking.bookings(self.pod, self.date_start, self.date_end)

    def get_form_view(self, client) -> ft.View:

        self.buttons.controls = [
            ft.ElevatedButton(_("Send"), on_click=lambda _: self.submit()),
            ft.ElevatedButton(_("Cancel"), on_click=lambda _: self.close()),
        ]
        column = ft.Column(
            controls=[
                self.email_input,
                self.email_errors,
                self.message,
                self.buttons
            ]
        )
        controls = [
            self.title,
            ft.Container(
                content=column,
                padding=20,
                margin=20
            )
        ]

        return client.get_view(
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

            # bookings = self.bookings.filter(email=booking.email)
            # if bookings.count():
            #     on_replace = self.on_replace(booking)
            #     return self.alert_dialog(on_replace, bookings)
            # else:
            self.save(booking)
        else:
            email_html_error = form.errors.get("email")

            if email_html_error:
                self.email_errors.value = email_html_error.as_text()
                self.update()

    # def alert_dialog(self, on_replace, bookings):
    #
    #     messages = [_("What too much is not healthy.")]
    #     word: str = _("You already have")
    #     for booking in bookings:
    #         messages.append(
    #             _("{word} the execution reserved for {term}.").format(word=word, term=booking.term_str))
    #         word = _("You have also")
    #
    #     messages.append(
    #         _("Do you want to cancel this date and book a new one?"))
    #
    #     self.title.value = _("Decide man!")
    #     self.message.value = " ".join(messages)
    #     self.buttons.controls = [
    #         ft.TextButton(_("Reject"), on_click=self.on_reset),
    #         ft.TextButton(_("Replace"), on_click=on_replace),
    #     ]
    #
    #     self.update()

    def save(self, booking):
        # if booking.count < 1:
        #     return self.message_dialog(
        #         message=_("The term already reserved, try another!"),
        #         title=_("Term is unavailable")
        #     )
        booking.save()
        # self.close()
        # message = _("""You reserved {pod} on the term {term}.
        # Confirm please within {expire} minutes by clicking on the link that you will find in an email sent to
        #  address {email}.
        # """).format(pod=self.pod, expire=EXPIRE_MINUTES, term=booking.term_str, email=booking.email)
        # self.message_dialog(
        #     message=message,
        #     title=_("We saved the reservation. We are waiting for confirmation.")
        # )

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

    def __call__(self, client: GenericClient):
        self.client = client
        return self.get_form_view(client)

    def close(self):
        if self.client:
            if self.client.dialog:
                self.client.dialog.open = False
            self.client.pop()
            # self.update()

    def update(self, *controls):
        self.client.update(*controls)

    def on_replace(self, booking: Booking):
        def __on_replace(*_):
            """TODO: use transaction here"""
            self.bookings.filter(email=booking.email).delete()
            self.save(booking)

        return __on_replace

    def on_reset(self, *_):
        self.close()
