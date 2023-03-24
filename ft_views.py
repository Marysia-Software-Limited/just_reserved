# This is a sample Python script.
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import openai as openai

from config import config
import requests
from PIL import Image
import io

import flet as ft
from flet_django import GenericApp
from flet_django import GenericClient
from flet_django import GenericViewFactory

from config import assets_dir


def get_pods():
    from pods.models import Pod
    return Pod.objects.all()


def home(client: GenericClient, pods_qs=get_pods):
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
            on_click=lambda _: client.go(calendar_url),
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
    return client.get_view(
        controls=[column],
    )


AI_IMG_STYLES = {
    "openai": "Free Creation",
    "abstract-painting-generator": "Abstract Painting",
    "steampunk-generator": "Steampunk",
    "cute-creature-generator": "Cute Creature",
    "fantasy-world-generator": "Fantasy",
    "cyberpunk-generator": "Cyberpunk",
    "anime-portrait-generator": "Portrait",
    "old-style-generator": "Old Style",
    "watercolor-architecture-generator": "Architecture",
    "text2img": "Image",
}


def openai_img_url(desc: str):
    openai.api_key = config.OPENAI_KEY

    query_response = openai.Image.create(
        prompt=f'{desc}',
        n=1,
        size="512x512"
    )
    return query_response['data'][0]['url']


def deepapi_img_url(desc: str, style: str):
    query_response = requests.post(
        f"https://api.deepai.org/api/{style}",
        data={
            'text': f'background, light, {desc}',
            'grid_size': "1"
        },
        headers={'api-key': config.DEEP_AI_API_KEY}
    ).json()
    return query_response['output_url']


class ViewFactory(GenericViewFactory):
    background: Optional[ft.Container] = None

    def generate_background(self, desc, style):


        try:
            if style == "openai":
                query_response_url = openai_img_url(desc)
            else:
                query_response_url = deepapi_img_url(desc, style)
        except Exception as _:
            return

        file_name = os.path.basename(urlparse(query_response_url).path)

        thumbails = assets_dir("thumbails")
        backgrounds = assets_dir("backgrounds")

        bg_file_path = str(backgrounds(file_name))
        th_file_path = str(thumbails(file_name))

        download_response = requests.get(query_response_url, allow_redirects=True)

        open(bg_file_path, 'wb').write(download_response.content)

        self.set_background(file_name)

        img = Image.open(bg_file_path)

        th_size = (300, 200)

        img.thumbnail(th_size, Image.ANTIALIAS)
        img.save(th_file_path, "JPEG")

    def set_background(self, file_name):
        self.bg_img = file_name

        self.background.image_src = self.bg_img
        self.background.update()

    def get_on_select(self, file_name):
        def __wrap_click(_):
            self.set_background(file_name)

        return __wrap_click

    @property
    def select_background(self):

        def close_dlg(e):
            dlg_modal.open = False
            self.client.update()

        def yes_dlg(e):
            desc = bg_desc.value
            style = bg_style.value
            close_dlg(e)
            self.generate_background(desc, style)

        bg_desc = ft.TextField(label="Describe what You expect on Your new background.")
        bg_style = ft.Dropdown(
            label="Style",
            hint_text="Select background style",
            options=[
                ft.dropdown.Option(name, text=label) for name, label in AI_IMG_STYLES.items()
            ]
        )

        modal_content = ft.Row(
            controls=[
                bg_desc,
                bg_style
            ],
            wrap=True
        )

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create new background"),
            content=modal_content,
            actions=[
                ft.TextButton("Generate background", on_click=yes_dlg),
                ft.TextButton("Cancel", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        def open_dlg(e):
            self.client.page.dialog = dlg_modal
            dlg_modal.open = True
            self.client.update()

        generate = ft.PopupMenuItem(
            content=ft.Text("Generate new background"),
            on_click=open_dlg
        )

        __select_background = ft.PopupMenuButton(
            items=[
                generate,
            ]
        )

        thumbails = assets_dir("thumbails")

        for img_file in thumbails:
            item = ft.PopupMenuItem(
                content=ft.Image(
                    src=f"/thumbails/{img_file.name}",
                    width=300,
                    height=200
                ),
                on_click=self.get_on_select(img_file.name)
            )
            __select_background.items.append(item)

        return __select_background

    def app_bar_factory(self, **app_bar_params):
        app_bar = super().app_bar_factory(**app_bar_params)
        app_bar.actions.append(self.select_background)
        return app_bar

    @property
    def bg_img(self):
        if not self.client.page.client_storage.contains_key("background"):
            self.client.page.client_storage.set("background", "bac10.png")
        return f"/backgrounds/{self.client.page.client_storage.get('background')}"

    @bg_img.setter
    def bg_img(self, file_name):
        self.client.page.client_storage.set("background", file_name)

    def get_view(self, controls, **kwargs):

        self.client.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD,
        )
        self.client.update()

        if len(controls) > 1:
            content = ft.Row(
                controls=controls,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                wrap=True
            )
        else:
            content = controls[0]

        self.background = ft.Container(
            image_src=self.bg_img,
            image_fit=ft.ImageFit.COVER,
            expand=True,
            border=ft.border.all(1, ft.colors.RED),
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
        view=lambda client: home(client, test_pods),
        view_factory=ViewFactory
    )

    ft.app(
        main,
        assets_dir="assets",
        view="web_browser",
        port=8550
    )

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
