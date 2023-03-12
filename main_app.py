import flet as ft
from django.urls import path
import flet_django as fdj

from pods.ft_views import services
from pods.models import Pod
from flet_django.pages import GenericApp
from flet_django.views import ft_view
from flet_django.middlewares import simple_view_middleware
from flet_django.navigation import Fatum

from ft_views import home, ViewFactory


app_bar_params = dict(bgcolor=ft.colors.SURFACE_VARIANT)
view_params = dict(app_bar_params=app_bar_params)


main = fdj.GenericApp(
    destinations=[
        fdj.Fatum("/", icon=ft.icons.HOME, label="home", action=False, nav_bar=True),
        fdj.Fatum("/services", icon=ft.icons.LIST_SHARP, label="reservation", action=False, nav_bar=True)
    ],
    urls=[
        path("", home),
        path("services", services),
        path("services/<int:pod_id>/", services)
    ],
    view_factory=ViewFactory,
    view_params=view_params,
)
