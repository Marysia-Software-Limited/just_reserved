from datetime import datetime
from typing import Optional

import flet as ft
from flet_django import *
from nptime import nptime

from pods.models import Pod
from .models import Booking, EXPIRE_MINUTES

from .forms import BookingEmailForm


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
            label="Email",
            helper_text="Podaj adres email aby zapisać swoją rezerwację."
        )
        self.error_message: ft.Control = ft.TextField()
        self.__form_dialog: Optional[ft.AlertDialog] = None
        self.__page: Optional[ft.Page] = None

    @property
    def dialog(self) -> Optional[ft.AlertDialog]:
        return self.__page.dialog if self.__page else None

    @dialog.setter
    def dialog(self, new_dialog: ft.AlertDialog):
        self.__page.dialog = new_dialog
        new_dialog.open = True
        self.update()

    @property
    def bookings(self):
        return Booking.bookings(self.pod, self.date_start, self.date_end)

    @property
    def form_dialog(self) -> ft.AlertDialog:
        if self.__form_dialog is not None:
            return self.__form_dialog

        content: ft.Control = self.email_input

        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Podaj swój email do rezerwacji"),
            content=content,
            actions=[
                ft.TextButton("Rezygnuj", on_click=lambda _:self.close()),
                ft.TextButton("Rezerwuj", on_click=lambda _:self.submit()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    def submit(self):
        data = {
            "email": self.email_input.value
        }
        form = BookingEmailForm(data)
        if form.is_valid():
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

    def alert_dialog(self, on_replace, bookings):

        messages = ["Co za dużo to niezdrowo."]
        word: str = "już"
        for booking in bookings:
            messages.append(
                f"Masz {word} zarezerwowaną egzekucję na {booking.term_str}.")
            word = "też"
        messages.append(
            f"Czy chcesz odwołać {'te terminy' if len(bookings) > 1 else 'ten termin'} i zarezerwować nowy?")

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Zdecyduj się człowieku!"),
            content=ft.Text(" ".join(messages)),
            actions=[
                ft.TextButton("Rezygnuj", on_click=self.on_reset),
                ft.TextButton("Zamień", on_click=on_replace),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    def save(self, booking):
        if booking.count < 1:
            return self.message_dialog(
                message="Termin już zarezerwowany, spróbuj inny",
                title="Termin niedostępny"
            )
        booking.save()
        message = f"""Zarezerwowałeś {booking.pod} w termine {booking.term_str}.
        Potwierdź proszę w przeciągu {EXPIRE_MINUTES} minut, klikając na link który znajdziesz w emailu wysłanym na 
        adres {booking.email}.
        """
        self.message_dialog(
            message=message,
            title="Zapisaliśmy rezerwację. Czekamy na potwierdzenie."
        )

    def message_dialog(
            self,
            message: str,
            title: str = "",
            button_text: str = "Dobra",
            on_click=None
    ):

        on_click = on_click or self.on_reset

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(button_text, on_click=on_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

    def __call__(self, page: GenericPage):
        self.__page = page.ft_page
        self.dialog = self.form_dialog

    def close(self):
        self.dialog.open = False
        self.update()
        self.__page = None

    def update(self):
        self.__page.update()

    def on_replace(self, booking: Booking):
        def __on_replace(*_):
            """TODO: use transaction here"""
            self.bookings.filter(email=booking.email).delete()
            self.save(booking)

        return __on_replace

    def on_reset(self, *_):
        self.close()
