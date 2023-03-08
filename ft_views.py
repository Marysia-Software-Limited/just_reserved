# This is a sample Python script.
from dataclasses import dataclass

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import flet as ft
from flet_django import ft_view
from flet_django import GenericApp
from flet_django import GenericPage


def get_pods():
    from pods.models import Pod
    return Pod.objects.all()


def home(page: GenericPage, pods_qs=get_pods):
    # page.ft_page.floating_action_button = ft.FloatingActionButton(
    #     icon=ft.icons.ADD,
    #     on_click=lambda _: None,
    # )
    # page.ft_page.scroll = ft.ScrollMode.ALWAYS
    # page.update()

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

    # column = ft.Column(
    #     alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    #     horizontal_alignment=ft.CrossAxisAlignment.CENTER
    # )

    # container = ft.Container(
    #     content=column,
    #     alignment=ft.alignment.center
    # )

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
    return ft_view(
        page=page,
        controls=[column],
    )


def get_view(controls, **kwargs):
    if len(controls) > 1:
        content = ft.Column(
            controls=controls,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    else:
        content = controls[0]
    controls = [
        ft.Container(
            image_src="/background22.png",
            image_fit=ft.ImageFit.COVER,
            expand=True,
            content=content
        ),
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
        view_factory=get_view
    )

    ft.app(
        main,
        assets_dir="assets",
        view="web_browser",
        port=8550
    )

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
