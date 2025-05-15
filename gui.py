import subprocess
import sys
import os
import time
import flet as ft
import yaml
import clean_groups
import webbrowser
import util
import gui_breakout_monitor

__version__ = "beta 0.3.1"
development_mode = False

t_rounds = ft.TextField(value=3, width=50, text_align=ft.TextAlign.CENTER)
t_checkin = ft.TextField(
    value=2,
    width=80,
    label="CheckIn",
    label_style=ft.TextStyle(size=15),
    suffix_text="min",
)
t_round_duration = ft.TextField(
    value=3,
    width=80,
    label="Round",
    label_style=ft.TextStyle(size=15),
    suffix_text="min",
)
t_fadeout = ft.TextField(
    value=2,
    width=80,
    label="Fadeout",
    label_style=ft.TextStyle(size=14),
    suffix_text="min",
)
l_total_time = ft.Text(value="--:--", size=15)
pb = ft.ProgressBar(width=210, value=1)
global t_info
t_info = ft.Text("", size=20)
t_currenttime = ft.Text("00:00", size=50)


c_ring_bell = ft.Switch(label="Ring bell in main room", value=True)
c_send_to_breakouts = ft.Switch(label="Send text to sessions", value=True)
t_send_to_breakouts = ft.TextField(
    value="{i}. person can start now ∞ {i}. Person kann jetzt beginnen"
)
t_send_to_breakouts_fadeout = ft.TextField(value="Fadeout ∞ Ausklingen")


# Titlecard controls
t_titlecard_time = ft.TextField(
    value="00:30",
    width=80,
    label="Break Time",
    label_style=ft.TextStyle(size=15),
    hint_text="HH:MM",
)
t_titlecard_image_path = ft.TextField(
    value="",
    label="Image Path",
    read_only=True,
    expand=True,
)


email = "max@thesharing.space"

# unique filename
t_settings_filename = f"temp_settings_{round(time.time())}.json"


def safe_settings(e):
    old_settings = get_settings()
    old_settings["group_size"] = int(dd_group_size.value)
    with open("settings.txt", "w") as f:
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
        "tags_hosts": ["Host", "\.:\.", "Team"],
        "tags_lang1": ["DE", "De-", "De ", "^de ", "^de-", "^de/", "D E "],
        "tags_lang2": ["EN", "En-", "En ", "ES", "SP"],
        "version": __version__,
    }
    with open("settings.txt", "w") as f:
        yaml.dump(settings, f, sort_keys=False, default_flow_style=False)
    return settings


def get_settings():
    try:
        with open("settings.txt") as f:
            settings = yaml.safe_load(f)
    except:
        print("Error loading settings, loading defaults")
        settings = reset_settings_file()
    return settings


dd_group_size = ft.Dropdown(
    border="UNDERLINE",
    width=50,
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
    util.save_t_values({"open": True}, t_settings_filename)

    def window_event(e):
        if e.data == "close":
            try:
                os.remove("t_settings.json")
            except:
                print("Timer already stopped")
            page.window_destroy()

    page.window_prevent_close = True
    page.on_window_event = window_event
    t = ft.Text()
    tabs = ft.Tab()
    page.snack_bar = ft.SnackBar(
        content=t,
        action="OK",
    )

    def save_user_inputs():
        user_inputs = {
            "t_checkin": t_checkin.value,
            "t_round": t_round_duration.value,
            "t_fadeout": t_fadeout.value,
            "t_rounds": t_rounds.value,
            "c_send_to_breakouts": c_send_to_breakouts.value,
            "c_ring_bell": c_ring_bell.value,
            "dd_group_size": dd_group_size.value,
            "t_send_to_breakouts_fadeout": t_send_to_breakouts_fadeout.value,
            "t_send_to_breakouts": t_send_to_breakouts.value,
            "c_sync_time_with_zoom": c_sync_time_with_zoom.selected,
            "t_titlecard_time": t_titlecard_time.value,
            "t_titlecard_image_path": t_titlecard_image_path.value,
            # Add more inputs here...
        }

        page.client_storage.set("user_inputs", user_inputs)

    def restore_user_inputs():
        user_inputs = page.client_storage.get("user_inputs")
        if not user_inputs:
            return

        t_checkin.value = user_inputs.get("t_checkin", t_checkin.value)
        t_round_duration.value = user_inputs.get("t_round", t_round_duration.value)
        t_fadeout.value = user_inputs.get("t_fadeout", t_fadeout.value)
        t_rounds.value = user_inputs.get("t_rounds", t_rounds.value)
        c_send_to_breakouts.value = user_inputs.get(
            "c_send_to_breakouts", c_send_to_breakouts.value
        )
        c_ring_bell.value = user_inputs.get("c_ring_bell", c_ring_bell.value)
        dd_group_size.value = user_inputs.get("dd_group_size", dd_group_size.value)
        t_send_to_breakouts_fadeout.value = user_inputs.get(
            "t_send_to_breakouts_fadeout", t_send_to_breakouts_fadeout.value
        )
        t_send_to_breakouts.value = user_inputs.get(
            "t_send_to_breakouts", t_send_to_breakouts.value
        )
        c_sync_time_with_zoom.selected = user_inputs.get(
            "c_sync_time_with_zoom", c_sync_time_with_zoom.selected
        )
        t_titlecard_time.value = user_inputs.get(
            "t_titlecard_time", t_titlecard_time.value
        )
        t_titlecard_image_path.value = user_inputs.get(
            "t_titlecard_image_path", t_titlecard_image_path.value
        )

        # Update the GUI controls with restored values
        page.update()

    def open_settings(e):
        if not os.path.exists("settings.txt"):
            reset_settings_file()

        webbrowser.open("settings.txt")

    def open_room_monitor(e):
        subprocess.run(sys.executable + " gui_breakout_monitor.py", shell=True)

    def on_tab_change(e):
        if tabs.selected_index != 0:
            page.floating_action_button.visible = False
            page.window_height = 540
            page.update()
            b.update()
            update_total_time(e)
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
            t.value = "Done"
        except Exception as e:
            # ... PRINT THE ERROR MESSAGE ... #
            t.value = e
            page.snack_bar.open = True
        b.disabled = False
        page.update()

    b = ft.FloatingActionButton(icon=ft.icons.PLAY_ARROW, on_click=play_button_clicked)

    def update_total_time(e):
        try:
            global checkin_duration
            checkin_duration = int(t_checkin.value)
            t_checkin.border_color = None
            t_checkin.value = checkin_duration
        except:
            t_checkin.border_color = "red"

        try:
            global fadeout_duration
            fadeout_duration = int(t_fadeout.value)
            t_fadeout.border_color = None
            t_fadeout.value = fadeout_duration
        except:
            t_fadeout.border_color = "red"

        try:
            global nr_of_rounds
            nr_of_rounds = int(t_rounds.value)
            t_rounds.border_color = None
            t_rounds.value = nr_of_rounds
        except:
            t_rounds.border_color = "red"

        try:
            global round_duration
            round_duration = int(t_round_duration.value)
            t_round_duration.border_color = None
            t_round_duration.value = round_duration
        except:
            t_round_duration.border_color = "red"

        try:
            total_time = (
                nr_of_rounds * round_duration + checkin_duration + fadeout_duration
            ) * 60
            l_total_time.value = str(total_time // 60) + ":00"
        except:
            total_time = 0
            l_total_time.value = "??:??"
        page.update()
        return total_time

    def send_to_breakouts(text):
        # open alert dialog before sending message
        def close_dlg(e):
            dlg_modal.open = False
            page.update()
            c_send_to_breakouts.value = False

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Sending Text to Breakouts..."),
            content=ft.Text("Sending Text: \n" + text),
            actions=[
                ft.TextButton("STOP", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()
        time.sleep(3)
        dlg_modal.open = False
        page.update()
        if c_send_to_breakouts.value:
            for _ in range(3):
                if util.send_text_to_zoom(text):
                    t.value = "Text was send " + text
                    page.snack_bar.open = True
                    page.update()
                    return True
                else:

                    def close_banner(e):
                        page.banner.open = False
                        page.update()

                    page.banner = ft.Banner(
                        bgcolor=ft.colors.AMBER_100,
                        leading=ft.Icon(
                            ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.RED, size=40
                        ),
                        content=ft.Text("Text was not send!. Retrying... \n" + text),
                        actions=[
                            ft.TextButton("close", on_click=close_banner),
                        ],
                    )
                    t.value = "Text was not send!. Retrying..."
                    # page.snack_bar.open = True
                    page.banner.open = True
                    page.update()
                    time.sleep(3)  # Wait for a second before retrying

    def enable_timer_inputs():
        b_start_timer.visible = True
        b_stop_timer.visible = False
        t_checkin.disabled = False
        t_fadeout.disabled = False
        t_round_duration.disabled = False
        t_rounds.disabled = False
        b_timer_fullscreen.visible = False
        c_sync_time_with_zoom.visible = True

    def disable_timer_inputs():
        b_start_timer.visible = False
        b_stop_timer.visible = True
        t_checkin.disabled = True
        t_fadeout.disabled = True
        t_round_duration.disabled = True
        t_rounds.disabled = True
        b_timer_fullscreen.visible = True
        c_sync_time_with_zoom.visible = False

    def push_timer_values_to_gui_timer_fullscreen():
        util.save_t_values(
            {
                "timer_running": True,
                "l_total_time": l_total_time.value,
                "pb": pb.value,
                "t_info": t_info.value,
                "t_currenttime": t_currenttime.value,
            },
            t_settings_filename,
        )

    def open_timer_fullsize(e):

        util.save_t_values(
            {"timer_running": True},
            t_settings_filename,
        )
        process = subprocess.run(
            [sys.executable, "gui_timer_fullscreen.py", t_settings_filename], shell=True
        )

        page.update()

    def start_timer(e):
        if l_total_time.value == "??:??":
            t.value = "Please check your inputs!"
            page.snack_bar.open = True
            page.update()
            return
        save_user_inputs()
        total_time = update_total_time(e)

        # mark timer as started
        util.save_t_values(
            {"timer_running": True},
            t_settings_filename,
        )

        disable_timer_inputs()

        t.value = "External audio shared?\nBreakout sessions window opened?"
        page.snack_bar.open = True
        page.update()
        i = 0
        global t_info
        start_time = time.time()

        sync_time_with_zoom = c_sync_time_with_zoom.selected
        try:
            if sync_time_with_zoom:
                # Define remaining total time
                remaining_total_time = (
                    util.get_time_left_in_breakouts()
                )  # (hours, minutes, seconds)
                # Convert remaining total time to seconds
                remaining_total_seconds = (
                    int(remaining_total_time[0]) * 3600
                    + int(remaining_total_time[1]) * 60
                    + int(remaining_total_time[2])
                )
                # calculate starting time
                start_time = time.time() - (total_time - remaining_total_seconds)

                # Calculate elapsed time since the start
                elapsed_time = time.time() - start_time

                # Determine in which phase you are
                if elapsed_time <= checkin_duration * 60:
                    phase = "Check-in"
                    phase_duration = checkin_duration * 60
                    round_number = 0  # No round during check-in
                else:
                    # Calculate elapsed time excluding check-in phase
                    elapsed_time -= checkin_duration * 60

                    # Determine the number of complete rounds and remaining time
                    complete_rounds = elapsed_time // (round_duration * 60)
                    remaining_time = elapsed_time % (round_duration * 60)

                    if complete_rounds < nr_of_rounds:
                        phase = "{i}. Person"
                        phase_duration = round_duration * 60
                        round_number = complete_rounds + 1
                    else:
                        phase = "Fadeout"
                        phase_duration = fadeout_duration * 60
                        round_number = t_rounds.value

                i = int(round_number)

                # Calculate time left in the current phase
                time_left_in_phase = phase_duration - (elapsed_time % phase_duration)
        except:
            sync_time_with_zoom = False
            print("connection to zoom breakout window failed")

        while i <= (t_rounds.value + 2):
            start_time_current_round = time.time()
            if not sync_time_with_zoom:
                if i == 0:
                    duration = int(t_checkin.value)
                    t_info.value = "Check in"
                elif i == 1:
                    duration = int(t_round_duration.value)
                    t_info.value = f"{i}. Person"
                    if c_send_to_breakouts.value:
                        send_to_breakouts(t_send_to_breakouts.value.format(i=i))

                elif i == t_rounds.value + 1:
                    duration = int(t_fadeout.value)
                    t_info.value = "Fadeout"
                    page.update(t_info)
                    if c_ring_bell.value:
                        util.make_a_sound()
                        util.make_a_sound()
                    if c_send_to_breakouts.value:
                        send_to_breakouts(t_send_to_breakouts_fadeout.value)
                elif i == t_rounds.value + 2:
                    duration = 0
                    page.update(t_info)
                    if c_ring_bell.value:
                        util.make_a_sound()
                        util.make_a_sound()
                        util.make_a_sound()
                else:
                    duration = int(t_round_duration.value)
                    t_info.value = f"{i}. Person"
                    if c_ring_bell.value:
                        util.make_a_sound()
                    if c_send_to_breakouts.value:
                        send_to_breakouts(t_send_to_breakouts.value.format(i=i))

            if sync_time_with_zoom:
                end_time = start_time_current_round + time_left_in_phase
                try:
                    t_info.value = phase.format(i=i)
                except:
                    t_info.value = phase

                sync_time_with_zoom = False
            else:
                end_time = start_time_current_round + duration * 60

            if development_mode:
                end_time = start_time_current_round + 5

            page.update(t_info)
            i += 1
            # Countdown loop
            while (
                util.load_t_values(t_settings_filename)["timer_running"]
                and time.time() < end_time
            ):
                total_end_time = start_time + total_time
                remaining_time = end_time - time.time()
                remaining_total_time = total_end_time - time.time()
                total_mins = int(remaining_total_time // 60)
                progress = 1 - remaining_total_time / total_time
                mins = int(remaining_time // 60)
                secs = int(remaining_time % 60)
                t_currenttime.value = f"{mins:02d}:{secs:02d}"
                l_total_time.value = f"{total_mins:02d}:{secs:02d}"
                pb.value = progress
                page.update()

                push_timer_values_to_gui_timer_fullscreen()

                time.sleep(1)
                # Check for "Stop Timer" button press
                if not "timer_running" in util.load_t_values(t_settings_filename):
                    i = t_rounds.value + 1
                    total_time = 0
                    t_currenttime.value = "00:00"
                    l_total_time.value = "00:00"
                    t_info.value = "Stopped"
                    enable_timer_inputs()
                    page.update()
                    return

        t_info.value = "Finished"
        t_currenttime.value = "00:00"
        l_total_time.value = "00:00"
        stop_timer(e)
        enable_timer_inputs()
        page.update()

    def stop_timer(e):
        util.delete_t_value("timer_running", t_settings_filename)

        # delete old temp files
        for filename in os.listdir():
            if (
                filename.startswith("temp_settings_")
                and filename.endswith(".json")
                and not t_settings_filename
            ):
                os.remove(filename)

    t_rounds.on_change = update_total_time
    t_checkin.on_change = update_total_time
    t_round_duration.on_change = update_total_time
    t_fadeout.on_change = update_total_time

    b_start_timer = ft.IconButton(
        icon=ft.icons.PLAY_ARROW_ROUNDED, on_click=start_timer
    )
    b_stop_timer = ft.IconButton(icon=ft.icons.STOP, on_click=stop_timer, visible=False)
    b_timer_fullscreen = ft.IconButton(
        icon=ft.icons.OPEN_IN_FULL, on_click=open_timer_fullsize, visible=False
    )

    def toggle_button(e):
        e.control.selected = not e.control.selected
        print(e.control.selected)
        e.control.update()

    c_sync_time_with_zoom = ft.IconButton(
        icon=ft.icons.SYNC_DISABLED,
        selected_icon=ft.icons.SYNC,
        selected=True,
        on_click=toggle_button,
    )

    timer = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        height=page.height,
        controls=[
            ft.Row([t_info, t_currenttime], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([pb, l_total_time]),
            ft.Row(
                [
                    b_start_timer,
                    b_stop_timer,
                    b_timer_fullscreen,
                    c_sync_time_with_zoom,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [t_checkin, t_round_duration, t_fadeout],
            ),
            ft.ListTile(
                leading=ft.Icon(ft.icons.GROUP),
                title=ft.Text("How many Rounds?"),
                trailing=t_rounds,
            ),
            ft.ListTile(title=c_send_to_breakouts),
            ft.ListTile(title=c_ring_bell),
        ],
    )

    def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        theme_switch.label = (
            "Enable Night Theme"
            if page.theme_mode == ft.ThemeMode.LIGHT
            else "Return To Day Theme"
        )
        page.update()

    page.theme_mode = ft.ThemeMode.LIGHT
    theme_switch = ft.Switch(label="Enable Night Theme", on_change=theme_changed)

    def close_dlg_reset_settings(e):
        dlg_reset_settings.open = False
        page.update()

    def reset_settings(e):
        print("Resetting Settings")
        page.client_storage.clear()
        reset_settings_file()
        close_dlg_reset_settings(e)
        page.window_close()
        os.execl("rcc.exe", "rcc.exe", "run")

    dlg_reset_settings = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to reset all settings?"),
        actions=[
            ft.TextButton("Yes", on_click=reset_settings),
            ft.TextButton("No", on_click=close_dlg_reset_settings),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    def open_dlg_reset_settings(e):
        page.dialog = dlg_reset_settings
        dlg_reset_settings.open = True
        page.update()

    b_delete_settings = ft.ElevatedButton(
        "Reset Settings",
        icon="delete",
        icon_color="red",
        on_click=open_dlg_reset_settings,
    )

    # Titlecard functions
    def pick_titlecard_image(e):
        def on_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                t_titlecard_image_path.value = e.files[0].path
                t_titlecard_image_path.update()
                save_user_inputs()

        file_picker = ft.FilePicker(on_result=on_result)
        page.overlay.append(file_picker)
        page.update()
        file_picker.pick_files(
            dialog_title="Pick an image for titlecard",
            file_type=ft.FilePickerFileType.IMAGE,
            allowed_extensions=["jpg", "jpeg", "png", "bmp"],
        )

    def open_titlecard(e):
        # Validate time format
        try:
            time_parts = t_titlecard_time.value.split(":")
            if len(time_parts) != 2 or not all(part.isdigit() for part in time_parts):
                raise ValueError("Invalid time format")

            # Check if image path exists
            if not t_titlecard_image_path.value or not os.path.exists(
                t_titlecard_image_path.value
            ):
                t.value = "Please select a valid image file first!"
                page.snack_bar.open = True
                page.update()
                return

            # Run the titlecard program
            subprocess.Popen(
                [
                    sys.executable,
                    "titlecard_image_with_breaktime.py",
                    t_titlecard_time.value,
                    t_titlecard_image_path.value,
                ],
                shell=True,
            )
            save_user_inputs()

        except ValueError:
            t.value = "Please enter a valid time in HH:MM format!"
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            t.value = f"Error: {str(ex)}"
            page.snack_bar.open = True
            page.update()

    b_pick_titlecard_image = ft.ElevatedButton(
        "Select Image",
        icon=ft.icons.IMAGE,
        on_click=pick_titlecard_image,
    )

    b_open_titlecard = ft.ElevatedButton(
        "Open Titlecard",
        icon=ft.icons.OPEN_IN_NEW,
        on_click=open_titlecard,
    )

    advanced_settings = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        spacing=0,
        controls=[
            ft.ExpansionTile(
                title=ft.Text("Timer", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                affinity=ft.TileAffinity.LEADING,
                initially_expanded=False,
                controls=[
                    ft.ListTile(
                        title=ft.Text("Switching to next person"),
                        subtitle=t_send_to_breakouts,
                    ),
                    ft.ListTile(
                        title=ft.Text("Fadeout started"),
                        subtitle=t_send_to_breakouts_fadeout,
                    ),
                ],
            ),
            ft.ExpansionTile(
                title=ft.Text("Titlecard", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                affinity=ft.TileAffinity.LEADING,
                initially_expanded=False,
                controls=[
                    ft.ListTile(
                        title=ft.Text("Break Duration"),
                        subtitle=ft.Text("Enter time in HH:MM format"),
                        trailing=t_titlecard_time,
                    ),
                    ft.ListTile(
                        title=ft.Text("Image File"),
                        subtitle=t_titlecard_image_path,
                    ),
                    ft.Row(
                        [b_pick_titlecard_image, b_open_titlecard],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
            ),
            ft.ExpansionTile(
                title=ft.Text("Other", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                affinity=ft.TileAffinity.LEADING,
                initially_expanded=True,
                controls=[
                    ft.ListTile(title=theme_switch),
                    ft.ListTile(title=b_delete_settings),
                ],
            ),
        ],
    )

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
                                leading=ft.Icon(ft.icons.GROUP),
                                title=ft.Text("Group Size"),
                                trailing=dd_group_size,
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.MONITOR_HEART_OUTLINED),
                                title=ft.Text("Room Monitor"),
                                on_click=open_room_monitor,
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.SETTINGS),
                                title=ft.Text("Advanced Settings"),
                                on_click=open_settings,
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=ft.padding.symmetric(vertical=0),
                ),
            ),
            ft.Tab(
                tab_content=ft.Icon(ft.icons.TIMER),
                content=timer,
            ),
            ft.Tab(
                tab_content=ft.Icon(ft.icons.SETTINGS),
                content=advanced_settings,
            ),
            ft.Tab(
                icon=ft.icons.INFO,
                content=ft.Column(
                    controls=[
                        ft.Text("Contact", size=18),
                        ft.Text(
                            "If you have any questions or suggestions, please contact me at:",
                        ),
                        ft.ListTile(
                            url="mailto:max@thesharingspace.de",
                            title=ft.Text("max@thesharingspace.de"),
                            on_click=email2clipboard,
                        ),
                        ft.Text("Support this project", size=18),
                        ft.Text(
                            "This project took many hours of work. Your support is highly appriciated <3",
                        ),
                        ft.ListTile(
                            title=ft.OutlinedButton(
                                icon=ft.icons.FAVORITE,
                                text="Donate",
                                url="https://www.paypal.com/paypalme/maxschwindt",
                                tooltip="paypal.me/maxschwindt",
                            )
                        ),
                        ft.Row(
                            [
                                ft.Text(
                                    "© 2022-"
                                    + str(time.gmtime(time.time()).tm_year)
                                    + " Max Schwindt"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.CODE,
                                    url="https://github.com/MaxWindt/zoom-triad-tool",
                                ),
                            ]
                        ),
                        ft.Text("Version: " + __version__),
                    ],
                    alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),
        ],
        width=400,
        height=500,
    )

    page.floating_action_button = b

    try:
        restore_user_inputs()
    except:
        print("no user input saved yet")

    page.add(tabs)


ft.app(target=gui)
