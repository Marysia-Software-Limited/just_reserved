# This is a sample Python script.
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from config import config
import requests
from PIL import Image
import io

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

    def generate_background(self, desc, style):
        query_response = requests.post(
            f"https://api.deepai.org/api/{style}",
            data={
                'text': f'background, light, {desc}',
                'grid_size': "1"
            },
            headers={'api-key': config.DEEP_AI_API_KEY}
        ).json()
        print(query_response['output_url'])

        thumbails = assets_dir("thumbails")
        backgrounds = assets_dir("backgrounds")

        file_name = f"{query_response['id']}-deepai.jpg"
        bg_file_path = str(backgrounds(file_name))
        th_file_path = str(thumbails(file_name))

        download_response = requests.get(query_response['output_url'], allow_redirects=True)

        open(bg_file_path, 'wb').write(download_response.content)

        self.set_background(file_name)

        img = Image.open(bg_file_path)

        th_size = (300, 200)

        img.thumbnail(th_size, Image.ANTIALIAS)
        img.save(th_file_path, "JPEG")

    def set_background(self, file_name):

        # backgrounds = assets_dir("backgrounds")
        # if file_name in backgrounds:
        #     self.page.session["background"] = f"/backgrounds/{file_name}"
        # else:
        #     self.page.session["background"] = f"/thumbails/{file_name}"
        self.page.session["background"] = f"/backgrounds/{file_name}"

        self.background.image_src = self.page.session["background"]
        self.background.update()

    def get_on_select(self, file_name):
        def __wrap_click(_):
            self.set_background(file_name)

        return __wrap_click

    @property
    def select_background(self):

        def close_dlg(e):
            dlg_modal.open = False
            self.page.update()

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
                ft.dropdown.Option("abstract-painting-generator", text="Abstract Painting"),
                ft.dropdown.Option("steampunk-generator", text="Steampunk"),
                ft.dropdown.Option("cute-creature-generator", text="Cute Creature"),
                ft.dropdown.Option("fantasy-world-generator", text="Fantasy"),
                ft.dropdown.Option("cyberpunk-generator", text="Cyberpunk"),
                ft.dropdown.Option("anime-portrait-generator", text="Portrait"),
                ft.dropdown.Option("old-style-generator", text="Old Style"),
                ft.dropdown.Option("watercolor-architecture-generator", text="Architecture"),
                ft.dropdown.Option("text2img", text="Image"),
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
            self.page.ft_page.dialog = dlg_modal
            dlg_modal.open = True
            self.page.update()

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

    def get_view(self, controls, **kwargs):

        if "background" not in self.page.session:
            self.page.session["background"] = "/backgrounds/bac10.png"

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
