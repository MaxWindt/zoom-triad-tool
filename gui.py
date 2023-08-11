import flet as ft
import yaml
import clean_groups
import webbrowser
import timer


def safe_gui_settings(e):
    old_settings = get_settings()
    old_settings["group_size"] = int(dd_group_size.value)
    with open('settings.txt', 'w') as f:
        yaml.dump(old_settings, f, sort_keys=False, default_flow_style=False)

def reset_settings_file():
    settings = {  # Version 1.0
        "group_size": 3,
        "minimal_group": 4,
        "placeholder_rooms": 5,
        "activate_language1": True,
        "activate_language2": True,
        "add_universal_to_language1": False,
        "add_universal_to_language2": False,
        "tags_nt": ["Triad", "TRIAD", "NT", "triad", "tirad", "^nt "],
        "tags_hosts": ["Host", ".:.", "Team"],
        "tags_lang1": ["DE", "De-", "De ", "^de ", "^de/", "D E "],
        "tags_lang2": ["EN", "En-", "En ", "ES", "SP"]}
    with open('settings.txt', 'w') as f:
        yaml.dump(settings, f, sort_keys=False, default_flow_style=False)
    return settings



def get_settings():
    try:
        with open('settings.txt') as f:
            settings = yaml.safe_load(f)
    except:
        print("Error loading settings, loading defaults")
        settings = reset_settings_file()
    return settings


dd_group_size = ft.Dropdown(border="UNDERLINE", width=50,
                            hint_text="Size",
                            on_change=safe_gui_settings,
                            value=3,
                            options=[
                                ft.dropdown.Option(2),
                                ft.dropdown.Option(3),
                                ft.dropdown.Option(6),
                            ],
                            )


def gui(page: ft.Page):
    page.title = "Triad Tool"
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_always_on_top = True
    page.window_width = 300
    page.window_height = 350
    t = ft.Text()
    tabs = ft.Tab()
    page.snack_bar = ft.SnackBar(
        content=t,
        action="OK",
    )

    def open_settings(e):
        webbrowser.open("settings.txt")

    def on_tab_change(e):
        if tabs.selected_index != 0:
            page.floating_action_button.visible = False
            page.window_height = 500
            page.update()
            b.update()
        else:
            page.floating_action_button.visible = True
            page.window_height = 300
            page.update()
            b.update()

    def play_button_clicked(e):
        b.disabled = True
        t.value = "working... do not interrupt!"
        b.update()
        try:
            # ... YOUR CODE HERE ... #
            clean_groups.main(get_settings())
            t.value = "Done"
        except Exception as e:
            # ... PRINT THE ERROR MESSAGE ... #
            t.value = e
            page.snack_bar.open = True
            page.update()
        b.disabled = False
        b.update()
        t.update()
    b = ft.FloatingActionButton(
        icon=ft.icons.PLAY_ARROW, on_click=play_button_clicked
    )
    pb = ft.ProgressBar(width=400, value=0.5)
    timer = ft.Column(
                scroll=ft.ScrollMode.ALWAYS,
                height=page.height,
                controls=[
                    ft.Row([ft.Text("1.", size=20),ft.Text("00:00", size=50)],alignment=ft.MainAxisAlignment.CENTER),
                    pb,
                    ft.Row(
                        [ft.IconButton(icon=ft.icons.PLAY_ARROW_ROUNDED), ft.IconButton(
                            icon=ft.icons.STOP)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.ListTile(
                        leading=ft.Icon(
                            ft.icons.GROUP),
                        title=ft.Text("Rounds"),
                        trailing=ft.TextField(
                            width=50, text_align=ft.TextAlign.CENTER),
                    ),
                    ft.ListTile(
                        leading=ft.Icon(
                            ft.icons.TIMELAPSE),
                        title=ft.Text("Time per Round (min)"),
                        trailing=ft.TextField(
                            width=50, text_align=ft.TextAlign.CENTER),
                    ),
                    ft.ListTile(
                        title=ft.Checkbox(label="Send Text To Breakouts")
                    ),
                    ft.ListTile(
                        title=ft.Checkbox(label="Ring Bell Every Round")
                    ),

                ]
            )


    tabs = ft.Tabs(
        selected_index=1,
        animation_duration=300,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(
                tab_content=ft.Icon(ft.icons.GROUPS),
                content=ft.Container(

                        content=ft.Column(
                            [

                                ft.ListTile(


                                    leading=ft.Icon(
                                        ft.icons.GROUP),
                                    title=ft.Text("Group Size"),
                                    trailing=dd_group_size,
                                ),
                                ft.ListTile(
                                    leading=ft.Icon(
                                        ft.icons.SETTINGS),
                                    title=ft.Text(
                                        "Advanced Settings"),
                                    on_click=open_settings
                                ),

                            ],
                            spacing=0,
                        ),
                        padding=ft.padding.symmetric(vertical=0),
                    )
                
            ),
            ft.Tab(
                tab_content=ft.Icon(ft.icons.TIMER),
                content=timer,
            ),
            ft.Tab(
                icon=ft.icons.INFO,
                content=ft.Text("Triad Tool v1.0"),
            ),
        ],
        width=400, height=500

    )

    page.floating_action_button = b
    txt_number = ft.TextField(value="0", text_align="center", width=50)
    page.add(tabs)


ft.app(target=gui)
