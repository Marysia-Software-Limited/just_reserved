# This is a sample Python script.
from dataclasses import dataclass
from typing import Optional

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import flet as ft
from flet_django import GenericApp
from flet_django import GenericPage
from flet_django import GenericViewFactory

from config import assets_dir


def get_pods():
    from pods.models import Pod
    return Pod.objects.all()


def home(page: GenericPage, pods_qs=get_pods):
    text = ft.Container(
        content=ft.Text(
            "This is not a regular app, like many others. This application is the first ever created and published in the newest, revolutionary Green Cloud Technology. Our outstanding Marysia Software team found a way to connect two well-established environments - Phyton -Django- and Dart -Flutter. It's just the first step, but the journey looks very promising. Try our Reservation App Demo and find out more on www.marysia.app.",
            font_family="Consolas",
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.BLACK,
        ),
        padding=50,
        margin=ft.margin.symmetric(horizontal=50),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.WHITE54, ft.colors.BLUE_GREY_400],
        ),
        border=ft.border.all(1, ft.colors.RED),
        width=600,
        opacity=1,
        border_radius=20,
    )

    controls = []

    image = ft.Image(
        src="/icons/logo1.png",
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,

    )

    controls.append(image)
    controls.append(text)

    for pod in pods_qs():
        calendar_url = f"services/{pod.pk}/"
        button = ft.ElevatedButton(
            pod.name,
            icon=ft.icons.CALENDAR_VIEW_WEEK,
            on_click=lambda _: page.go(calendar_url),
        )
        if pod.label:
            button.tooltip = pod.label
        button_container = ft.Container(
            content=button,
            padding=10,
            margin=10,
        )
        controls.append(button_container)

    column = ft.Column(
        controls=controls,
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.END,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    return page.get_view(
        controls=[column],
    )


class ViewFactory(GenericViewFactory):
    background: Optional[ft.Container] = None

    def set_background(self, file_name):

        backgrounds = assets_dir("backgrounds")
        if file_name in backgrounds:
            self.page.session["background"] = f"/backgrounds/{file_name}"
        else:
            self.page.session["background"] = f"/thumbails/{file_name}"

        self.background.image_src = self.page.session["background"]
        self.background.update()

    def get_on_select(self, file_name):
        def __wrap_click(_):
            self.set_background(file_name)

        return __wrap_click

    @property
    def select_background(self):
        __select_background = ft.PopupMenuButton(
            items=[]
        )

        thumbails = assets_dir("thumbails")

        for img_file in thumbails:
            item = ft.PopupMenuItem(
                content=ft.Image(
                    src=f"/thumbails/{img_file.name}",
                    width=240,
                    height=180
                ),
                on_click=self.get_on_select(img_file.name)
            )
            __select_background.items.append(item)

        return __select_background

    def app_bar_factory(self, **app_bar_params):
        app_bar = super().app_bar_factory(**app_bar_params)
        app_bar.actions.append(self.select_background)
        return app_bar

    def get_view(self, controls, **kwargs):

        if "background" not in self.page.session:
            self.page.session["background"] = "/backgrounds/background22.png"

        self.page.ft_page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD,
        )
        self.page.update()

        if len(controls) > 1:
            content = ft.Column(
                controls=controls,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            content = controls[0]

        self.background = self.background or ft.Container(
            image_src=self.page.session["background"],
            image_fit=ft.ImageFit.COVER,
            expand=True,
            content=content
        )

        controls = [
            self.background,
        ]

        return ft.View(controls=controls, padding=0, **kwargs)


if __name__ == '__main__':
    def test_pods():
        @dataclass
        class TestPod:
            pk: int
            name: str
            label: str

        return [
            TestPod(pk=1, name="ala", label="ala ma kota"),
            TestPod(pk=2, name="ela", label="ela ma kota"),
            TestPod(pk=3, name="ula", label="ula ma kota"),
            TestPod(pk=4, name="ola", label="ola ma kota"),
        ]


    main = GenericApp(
        view=lambda page: home(page, test_pods),
        view_factory=ViewFactory
    )

    ft.app(
        main,
        assets_dir="assets",
        view="web_browser",
        port=8550
    )

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
