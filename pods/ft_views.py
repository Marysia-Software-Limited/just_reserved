from datetime import time, timedelta, date, datetime

from flet_core import event
from flet_django import ft_view
import flet as ft
from nptime import nptime

from .models import Pod, Service
from bookings.controls import BookingFormView

TESTING_EMAIL = "beret@hipisi.org.pl"


def services(page):
    pod = Pod.objects.first()
    service = Service.objects.first()
    return calendar(page, pod.pk, service.pk)


def calendar(page, pod_id, service_id, start_date=datetime.now()):
    pod = Pod.objects.get(pk=pod_id)
    service = Service.objects.get(pk=service_id)

    def on_click_week(_):
        calendar_control.calendar_format = ft.CalendarFormat.WEEK
        page.update()

    week_button = ft.ElevatedButton(
        "Week",
        icon=ft.icons.CALENDAR_VIEW_WEEK,
        on_click=on_click_week,
    )

    def on_click_month(_):
        calendar_control.calendar_format = ft.CalendarFormat.MONTH
        page.update()

    month_button = ft.ElevatedButton(
        "Month",
        icon=ft.icons.CALENDAR_MONTH,
        on_click=on_click_month,
    )

    def on_day_selected(__calendar):
        def __on_day_selected(_event: event.Event):
            print(__calendar)
            selected_date = datetime.fromisoformat(_event.data)
            calendar_slots.content = make_slots_row(selected_date)
            page.update()

        return __on_day_selected

    calendar_control = ft.TableCalendar(
        current_day=start_date,
        first_day=datetime.now(),
        calendar_format=ft.CalendarFormat.WEEK,
    )
    calendar_control.on_day_selected = on_day_selected(calendar_control)
    calendar_title_row = ft.Row(
        controls=[week_button, month_button, ft.Text(pod)]
    )

    calendar_column = ft.Column(
        controls=[
            calendar_title_row,
            calendar_control
        ]
    )

    def make_slots(calendar_date):
        calendar_date = datetime(day=calendar_date.day, month=calendar_date.month, year=calendar_date.year)

        def slot(slot_time: nptime):
            label = f"{slot_time.hour:02d}:{slot_time.minute:02d}"

            booking_form = BookingFormView(
                calendar_date=calendar_date,
                time=slot_time,
                duration=service.slot,
                pod=pod
            )

            button = ft.ElevatedButton(
                label,
                icon=ft.icons.ACCESS_TIME,
                tooltip=service,
                on_click=lambda _: booking_form(page)
            )
            return button

        return map(slot, service.slots(pod))

    def make_slots_row(calendar_date):
        slots = make_slots(calendar_date)
        return ft.Row(
            controls=list(slots),
            expand=1,
            wrap=True,
        )

    calendar_card = ft.Card(content=calendar_column)

    calendar_slots = ft.Card(
        content=make_slots_row(start_date)
    )

    controls = [
        calendar_card,
        calendar_slots
    ]

    return ft_view(
        page=page,
        controls=controls,
    )
