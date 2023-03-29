from datetime import datetime
from typing import Optional

from flet_core import event
from flet_django import GenericClient
import flet as ft
from nptime import nptime


from bookings.models import Booking
from utils import day
from .models import Pod, Service
from bookings.controls import BookingFormView

from flet_calendar_control import CalendarControl

TESTING_EMAIL = "beret@hipisi.org.pl"


def services(client: GenericClient, pod_id: Optional[int] = None):
    if pod_id:
        pod = Pod.objects.get(pk=pod_id)
    else:
        pod = Pod.objects.first()
    service = Service.objects.first()
    return calendar(client, pod.pk, service.pk)


def calendar(client: GenericClient, pod_id, service_id, start_date=datetime.now()):
    pod = Pod.objects.get(pk=pod_id)
    service = Service.objects.get(pk=service_id)
    calendar_slots = ft.Row(
            # expand=1,
            wrap=True,
        )

    def make_slots(_date):
        _date = day(_date)
        slots = service.slots(pod)

        def slot(slot_time: nptime):
            label = f"{slot_time.hour:02d}:{slot_time.minute:02d}"

            booking_form = BookingFormView(
                calendar_date=_date,
                time=slot_time,
                duration=service.slot,
                pod=pod
            )

            booking = Booking(
                pod=pod,
                date_start=booking_form.date_start,
                date_end=booking_form.date_end
            )

            def on_click(*_):
                return None
            disable = True

            if booking.count > 0:
                def __open_form(*_):
                    client.append_view(booking_form)
                    client.update()

                on_click = __open_form
                disable = False

            button = ft.ElevatedButton(
                label,
                icon=ft.icons.ACCESS_TIME,
                tooltip=service,
                on_click=on_click,
                disabled=disable,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    color={
                        ft.MaterialState.DISABLED: ft.colors.RED,
                        ft.MaterialState.DEFAULT: ft.colors.GREEN,
                    },
                )
            )
            return button

        return list(map(slot, slots))

    def update_date(_date):
        calendar_slots.controls = make_slots(_date)

    update_date(start_date)

    def on_day_selected(_date):
        def __on_day_selected(_event: event.Event):
            update_date(_date)
            client.update()

        return __on_day_selected

    _calendar_control = CalendarControl(
        initial_date=start_date,
    )
    _calendar_control.on_select = on_day_selected

    calendar_title_text = ft.Text(
            pod,
            font_family="Consolas",
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.BLACK,
            size=22,
        )

    # calendar_title_row = ft.Row(
    #     controls=[
    #         ft.Text(
    #             pod,
    #             text_align=ft.TextAlign.CENTER
    #         )
    #     ],
    #     vertical_alignment=ft.alignment.center
    # )

    controls = [
        calendar_title_text,
        _calendar_control,
        calendar_slots,
    ]

    column = ft.Column(
        controls=controls,
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    calendar_content = ft.Container(
        content=column,
        padding=50,
        # margin=ft.margin.symmetric(horizontal=50),
        # gradient=ft.LinearGradient(
        #     begin=ft.alignment.top_center,
        #     end=ft.alignment.bottom_center,
        #     colors=[ft.colors.WHITE54, ft.colors.BLUE_GREY_400],
        # ),
        # border=ft.border.all(1, ft.colors.RED),
        width=600,
        # opacity=1,
        # border_radius=20,
    )

    return client.get_view(
        controls=controls,
    )
