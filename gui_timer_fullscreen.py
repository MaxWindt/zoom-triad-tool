import os
import time
import flet as ft
import tkinter as tk
import util


def get_screen_resolution():
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()  # Destroy the temporary Tkinter window
    return screen_width, screen_height


# Example usage:
screen_width, screen_height = get_screen_resolution()

l_total_time = ft.Text(value="--:--", size=15)
pb = ft.ProgressBar(width=210, value=1)
t_info = ft.Text("", size=20)
t_currenttime = ft.Text("00:00", size=50)

original_width = 300


def main(page: ft.Page):
    page.title = "Timer"

    def adjust_widths(e):
        relative_size = page.window_width / original_width

        # Adjust Text and ProgressBar width
        l_total_time.size = int(15 * relative_size)  # Adjust the width of the Text
        pb.width = int(210 * relative_size)  # Adjust the width of the ProgressBar
        pb.height = int(4 * relative_size)  # Adjust the height
        # Scale Text size
        t_info.size = int(20 * relative_size)
        t_currenttime.size = int(50 * relative_size)

        page.update()

    page.window_frameless = True
    page.window_width = screen_width
    page.window_height = screen_height
    # page.window_minimized = True
    page.on_resize = adjust_widths

    page.add(
        ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            height=page.height,
            controls=[
                ft.Row(
                    [t_info, t_currenttime],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row([pb, l_total_time], alignment=ft.MainAxisAlignment.CENTER),
            ],
        )
    )
    page.update()

    while (
        os.path.isfile(util.temp_settings_filename)
        and "timer_running" in util.load_t_values()
    ):
        time.sleep(1)
        try:
            values = util.load_t_values()
            l_total_time.value = values["l_total_time"]
            pb.value = values["pb"]
            t_info.value = values["t_info"]
            t_currenttime.value = values["t_currenttime"]

            page.update()
        except:
            print("Timer not running")

    page.window_destroy()


if __name__ == "__main__":
    # main()
    # name_list = get_active_breakout_list()
    # saved_list = np.load("active_breakouts_coregroup.npy")
    # np.save("active_breakouts_coregroup.npy", name_list)
    # room_details = get_language_of_group(name_list)

    # Run the app with the main function
    ft.app(target=main)
