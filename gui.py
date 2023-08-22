import time
import flet as ft
import yaml
import clean_groups
import clean_groups
import webbrowser
import timer_old
import util


__version__ = 'beta 1.1.0'
development_mode = False

t_rounds = ft.TextField(value=3, width=50, text_align=ft.TextAlign.CENTER)
t_checkin = ft.TextField(value=2, width=80, label="CheckIn",
                         label_style=ft.TextStyle(size=15), suffix_text="min")
t_round = ft.TextField(value=3, width=80, label="Round",
                       label_style=ft.TextStyle(size=15), suffix_text="min")
t_fadeout = ft.TextField(value=2, width=80, label="Fadeout",
                         label_style=ft.TextStyle(size=14), suffix_text="min")
l_total_time = ft.Text(value="--:--", size=15)
pb = ft.ProgressBar(width=215, value=1)
global t_info
t_info = ft.Text("", size=20)
t_currenttime = ft.Text("00:00", size=50)


c_ring_bell = ft.Switch(
    label="Ring Bell Every Round", value=True)
c_send_to_breakouts = ft.Switch(
    label="Send Text To Breakouts", value=True)

email = "max@thesharing.space"


def safe_settings(e):
    old_settings = get_settings()
    old_settings["group_size"] = int(dd_group_size.value)
    with open('settings.txt', 'w') as f:
        yaml.dump(old_settings, f, sort_keys=False, default_flow_style=False)
    t_rounds.value = dd_group_size.value
    t_rounds.update()


def reset_settings_file():
    settings = {
        "group_size": 3,
        "minimal_group": 2,
        "placeholder_rooms": 5,
        "activate_language1": True,
        "activate_language2": True,
        "add_universal_to_language1": True,
        "add_universal_to_language2": True,
        "tags_nt": ["Triad", "TRIAD", "NT", "triad", "tirad", "^nt "],
        "tags_hosts": ["Host", ".:.", "Team"],
        "tags_lang1": ["DE", "De-", "De ", "^de ", "^de/", "D E "],
        "tags_lang2": ["EN", "En-", "En ", "ES", "SP"],
        "version":__version__}
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
        settings = reset_settings_file()
    return settings


dd_group_size = ft.Dropdown(border="UNDERLINE", width=50,
                            hint_text="Size",
                            on_change=safe_settings,
                            value=3,
                            options=[
                                ft.dropdown.Option(2),
                                ft.dropdown.Option(3),
                                ft.dropdown.Option(6),
                            ],
                            )


def gui(page: ft.Page):
    page.title = "Triad Tool"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_always_on_top = True
    page.window_width = 300
    page.window_height = 300
    t = ft.Text()
    tabs = ft.Tab()
    page.snack_bar = ft.SnackBar(
        content=t,
        action="OK",
    )

    def save_user_inputs():
        user_inputs = {
            "t_checkin": t_checkin.value,
            "t_round": t_round.value,
            "t_fadeout": t_fadeout.value,
            "t_rounds": t_rounds.value,
            "c_send_to_breakouts": c_send_to_breakouts.value,
            "c_ring_bell": c_ring_bell.value,
            "dd_group_size": dd_group_size.value,
            # Add more inputs here...
        }

        page.client_storage.set("user_inputs", user_inputs)

    def restore_user_inputs():
        user_inputs = page.client_storage.get("user_inputs")

        t_checkin.value = user_inputs.get("t_checkin", t_checkin.value)
        t_round.value = user_inputs.get("t_round", t_round.value)
        t_fadeout.value = user_inputs.get("t_fadeout", t_fadeout.value)
        t_rounds.value = user_inputs.get("t_rounds", t_rounds.value)
        c_send_to_breakouts.value = user_inputs.get(
            "c_send_to_breakouts", c_send_to_breakouts.value)
        c_ring_bell.value = user_inputs.get("c_ring_bell", c_ring_bell.value)
        dd_group_size.value = user_inputs.get(
            "dd_group_size", dd_group_size.value)
        # Restore more inputs here...

        # Update the GUI controls with restored values
        page.update()

    def open_settings(e):
        webbrowser.open("settings.txt")

    def open_timer(e):
        timer_old.main()

    def on_tab_change(e):
        if tabs.selected_index != 0:
            page.floating_action_button.visible = False
            page.window_height = 540
            page.update()
            b.update()
        else:
            page.floating_action_button.visible = True
            page.window_height = 300
            page.update()
            b.update()

    def play_button_clicked(e):
        save_user_inputs()
        b.disabled = True
        t.value = "working... do not interrupt!"
        b.update()
        try:
            # ... YOUR CODE HERE ... #
            clean_groups.main(get_settings())
            clean_groups.main(get_settings())
            t.value = "Done"
        except Exception as e:
            # ... PRINT THE ERROR MESSAGE ... #
            t.value = e
            page.snack_bar.open = True
        b.disabled = False
        page.update()

    b = ft.FloatingActionButton(
        icon=ft.icons.PLAY_ARROW, on_click=play_button_clicked
    )

    def update_total_time(e):
        checkin = int(t_checkin.value)
        t_checkin.value = checkin
        checkout = int(t_fadeout.value)
        t_fadeout.value = checkout
        rounds = int(t_rounds.value)
        t_rounds.value = rounds
        round_duration = int(t_round.value)
        t_round.value = round_duration

        total_time = (rounds * round_duration + checkin + checkout) * 60
        l_total_time.value = str(total_time // 60) + ":00"
        page.update()
        return total_time

    def start_timer(e):
        save_user_inputs()
        total_time = update_total_time(e)
        global timer_event
        timer_event = ""

        timer_running = True
        b_start_timer.disabled = True
        b_stop_timer.disabled = False
        page.update()
        i = 0
        global t_info
        total_end_time = time.time() + total_time
        while i <= (t_rounds.value + 1):
            if i == 0:
                duration = int(t_checkin.value)
                t_info.value = "Check in"
            elif i == 1:
                duration = int(t_round.value)
                t_info.value = f"{i}. Person"
                if c_send_to_breakouts.value:
                    util.send_to_breakouts(
                        str(i)+". person can start now ∞ "+str(i)+". Person kann jetzt beginnen")
            elif i == t_rounds.value + 1:
                duration = int(t_fadeout.value)
                t_info.value = "Fadeout"
                page.update(t_info)
                if c_send_to_breakouts.value:
                    util.send_to_breakouts("Fadeout ∞ Ausklingen")
                if c_ring_bell.value:
                    util.make_a_sound()
                    time.sleep(4)
                    util.make_a_sound()
                    time.sleep(4)
                    util.make_a_sound()
            else:
                duration = int(t_round.value)
                t_info.value = f"{i}. Person"
                if c_ring_bell.value:
                    util.make_a_sound()
                if c_send_to_breakouts.value:
                    util.send_to_breakouts(
                        str(i)+". person can start now ∞ "+str(i)+". Person kann jetzt beginnen")
            page.update(t_info)
            i += 1
            end_time = time.time() + duration * 60
            if development_mode:
                end_time = time.time() + 5
            # countdown loop

            while timer_running and time.time() < end_time:
                remaining_time = end_time - time.time()
                remaining_total_time = total_end_time - time.time()
                total_mins = int(remaining_total_time // 60)
                progress = 1-remaining_total_time/total_time
                mins = int(remaining_time // 60)
                secs = int(remaining_time % 60)
                t_currenttime.value = f"{mins:02d}:{secs:02d}"
                l_total_time.value = f"{total_mins:02d}:{secs:02d}"
                pb.value = progress
                page.update()
                time.sleep(1)
                # Check for "Stop Timer" button press
                if timer_event == "Stop Timer":
                    i = t_rounds.value + 1
                    timer_running = False
                    total_time = 0
                    t_currenttime.value = "00:00"
                    b_start_timer.disabled = False
                    b_stop_timer.disabled = True
                    t_info.value = "Stopped"
                    break

            else:
                t_info.value = f"Finished"
                t_currenttime.value = "00:00"
                b_start_timer.disabled = False
                b_stop_timer.disabled = True

        page.update()

    def stop_timer(e):
        global timer_event
        timer_event = "Stop Timer"
        timer_running = False

    b_start_timer = ft.IconButton(
        icon=ft.icons.PLAY_ARROW_ROUNDED, on_click=start_timer)
    b_stop_timer = ft.IconButton(icon=ft.icons.STOP, on_click=stop_timer)
    timer = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        height=page.height,
        controls=[
            ft.Row([t_info, t_currenttime],
                   alignment=ft.MainAxisAlignment.CENTER),

            ft.Row([pb, l_total_time]),
            ft.Row(
                [b_start_timer, b_stop_timer],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row([t_checkin, t_round, t_fadeout],
                   ),
            ft.ListTile(
                leading=ft.Icon(
                    ft.icons.GROUP),
                title=ft.Text("How many Rounds?"),
                trailing=t_rounds,
            ),
            ft.ListTile(
                title=c_send_to_breakouts
            ),
            ft.ListTile(
                title=c_ring_bell
            ),

        ]
    )

    def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        theme_switch.label = (
            "Enable Night Theme" if page.theme_mode == ft.ThemeMode.LIGHT else "Return To Day Theme"
        )
        page.update()

    page.theme_mode = ft.ThemeMode.LIGHT
    theme_switch = ft.Switch(
        label="Enable Night Theme", on_change=theme_changed)

    def email2clipboard(e):
        page.set_clipboard(email)
        t.value = "Address Copied!"
        page.snack_bar.open = True
        page.update()

    tabs = ft.Tabs(
        selected_index=0,
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
                            ft.ListTile(


                                leading=ft.Icon(ft.icons.AV_TIMER),
                                title=ft.Text("The Old Timer"), on_click=open_timer
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
                content=ft.Column(
                    controls=[
                        ft.ListTile(
                            title=theme_switch
                        ),
                        ft.Text("Contact", size=18),
                        ft.Text(
                            "If you have any questions or suggestions, please contact me at:",
                        ),
                        ft.ListTile(url="mailto:max@thesharing.space",
                                    title=ft.Text("max@thesharing.space"), on_click=email2clipboard
                                    ),
                        ft.Text("Support this project", size=18),
                        ft.Text(
                            "This project took many hours of work. Your support is highly appriciated <3",
                        ),

                        ft.ListTile(
                            title=ft.OutlinedButton(icon=ft.icons.FAVORITE, 
                                                text="Donate", url="https://www.paypal.com/paypalme/maxschwindt", tooltip="paypal.me/maxschwindt",)
                        ),
                        ft.Row([ft.Text("© 2022-" + str(time.gmtime(time.time()).tm_year) + " Max Schwindt"), ft.IconButton(icon=ft.icons.CODE, url="https://github.com/MaxWindt/zoom-triad-tool")]),
                        ft.Text("Version: " + __version__)],
                    alignment=ft.CrossAxisAlignment.CENTER,

                ),
            ),
        ],
        width=400, height=500

    )

    page.floating_action_button = b

    try:
        restore_user_inputs()
    except:
        print("no user input saved yet")

    page.add(tabs)


ft.app(target=gui)
