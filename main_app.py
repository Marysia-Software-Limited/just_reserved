import flet as ft
from django.urls import path
import flet_django as fdj

from pods.ft_views import services
from pods.models import Pod
# from flet_django.pages import GenericApp
# from flet_django.views import ft_view
# from flet_django.middlewares import simple_view_middleware
# from flet_django.navigation import Fatum


def home(page):
    controls = []

    for pod in Pod.objects.all():
        button = ft.ElevatedButton(
            pod.name,
            icon=ft.icons.CALENDAR_VIEW_WEEK,
            on_click=lambda _: page.go("services"),
        )
        if pod.label:
            button.tooltip = pod.label
        controls.append(button)

    return fdj.ft_view(
        page=page,
        controls=controls,
    )


main = fdj.GenericApp(
    destinations=[
        fdj.Fatum("/", icon=ft.icons.HOME, label="home"),
        fdj.Fatum("/services", icon=ft.icons.LIST_SHARP, label="menu")
    ],
    urls=[
        path("", home),
        path("services", services)
    ]
)
