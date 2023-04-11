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

    text_content = ft.Text(
            "This is not a regular app, like many others. This application is the first ever created and published in the newest, revolutionary Green Cloud Technology. Our outstanding Marysia Software team found a way to connect two well-established environments Django, Flutter and one Python to rule them all. It's just the first step, but the journey looks very promising. Play with backgrounds, find what else can be edited and book your FREE, one-to-one consultation. Find more on https://www.marysia.app",
            font_family="Consolas",
            text_align=ft.TextAlign.CENTER,
            color=ft.colors.BLACK,
        )

    def on_text_change(e):
        text_content.value = text_edit.value
        text_content.update()

    text_edit = ft.TextField(
        value=text_content.value,
        on_change=on_text_change
    )

    bs_edit = ft.Row(
        wrap=True,
        controls=[
            text_edit,
            ft.ElevatedButton(
                text="Finish Editing",
                on_click=lambda _: client.bs.hide()
            )
        ]
    )

    def open_edit(*_):
        client.bs = bs_edit

    text = ft.Container(
        content=text_content,
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
        on_click=open_edit
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
    def edit_page(self):
        return ft.IconButton(
            icon=ft.icons.MODE_EDIT,
            tooltip="Edit page"
        )

    @property
    def add_page(self):
        return ft.IconButton(
            icon=ft.icons.ADD_CARD,
            tooltip="Add new page"
        )

    @property
    def select_background(self):

        def yes_dlg(_):
            desc = bg_desc.value
            style = bg_style.value
            self.client.dialog.hide()
            self.generate_background(desc, style)

        generate_button = ft.TextButton("Generate background", on_click=yes_dlg, disabled=True)

        def on_change(_):
            generate_button.disabled = False
            self.client.update()

        bg_desc = ft.TextField(label="Describe what You expect on Your new background.")
        bg_style = ft.Dropdown(
            label="Select style",
            hint_text="Select background style",
            options=[
                ft.dropdown.Option(name, text=label) for name, label in AI_IMG_STYLES.items()
            ],
            on_change=on_change
        )

        modal_content = ft.Row(
            controls=[
                bg_desc,
                bg_style
            ],
            wrap=True
        )

        modal_actions = [
            generate_button,
            ft.TextButton("Cancel", on_click=lambda _: self.client.dialog.hide()),
        ]

        def open_dlg(e):
            self.client.update_dialog(
                modal_content,
                modal_actions,
                show=True,
                title="Describe Your Background"
            )

        generate = ft.PopupMenuItem(
            content=ft.Text("Generate new background"),
            on_click=open_dlg
        )

        __select_background = ft.PopupMenuButton(
            items=[
                generate,
            ],

            content=ft.Icon(
                name=ft.icons.EDIT_DOCUMENT,
                tooltip="Edit background"
            ),
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
        # app_bar.actions.append(self.edit_page)
        # app_bar.actions.append(self.add_page)
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

        # self.client.page.floating_action_button = ft.FloatingActionButton(
        #     icon=ft.icons.ADD,
        # )
        # self.client.update()

        self.client.page.theme = ft.Theme(
            font_family="Consolas",
            color_scheme_seed=ft.colors.GREEN
        )

        if len(controls) > 1:
            content_row = ft.Row(
                controls=controls,
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                wrap=True,
                height=600
            )
            content = ft.Container(
                    content=content_row,
                    # padding=50,
                    margin=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[ft.colors.WHITE54, ft.colors.BLUE_GREY_400],
                    ),
                    border=ft.border.all(1, ft.colors.BLUE),
                    width=600,
                    height=640,
                    opacity=1,
                    border_radius=20,
                    alignment=ft.alignment.center
                )
        else:
            content = controls[0]

        self.background = ft.Container(
            image_src=self.bg_img,
            image_fit=ft.ImageFit.COVER,
            expand=True,
            border=ft.border.all(1, ft.colors.RED),
            content=content,
            alignment=ft.alignment.center
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
