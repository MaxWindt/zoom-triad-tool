import os
import time
import flet as ft
import tkinter as tk
import util
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="timer_app.log",
)


def get_screen_resolution():
    """Get the screen resolution using tkinter."""
    try:
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()  # Destroy the temporary Tkinter window
        return screen_width, screen_height
    except Exception as e:
        logging.error(f"Error getting screen resolution: {e}")
        return 1280, 720  # Fallback resolution


# Get screen dimensions with error handling
try:
    screen_width, screen_height = get_screen_resolution()
    logging.info(f"Screen resolution: {screen_width}x{screen_height}")
except Exception as e:
    logging.error(f"Failed to get screen resolution: {e}")
    screen_width, screen_height = 1280, 720  # Fallback values

# UI elements with default values
l_total_time = ft.Text(value="--:--", size=15)
pb = ft.ProgressBar(width=210, value=1)
t_info = ft.Text("", size=20)
t_currenttime = ft.Text("00:00", size=50)
original_width = 300
update_interval = 1  # Update interval in seconds


def load_timer_values(t_settings_filename) -> Dict[str, Any]:
    """
    Load timer values with robust error handling.

    Returns:
        Dict containing timer values or default values if loading fails
    """
    default_values = {
        "l_total_time": "--:--",
        "pb": 1,
        "t_info": "Timer Ready",
        "t_currenttime": "00:00",
        "timer_running": False,
    }

    try:
        if not os.path.isfile(t_settings_filename):
            logging.warning(f"Settings file not found: {t_settings_filename}")
            return default_values

        values = util.load_t_values(t_settings_filename)

        # Validate all required keys exist
        required_keys = ["l_total_time", "pb", "t_info", "t_currenttime"]
        for key in required_keys:
            if key not in values:
                logging.warning(f"Missing key in timer values: {key}")
                values[key] = default_values[key]

        # Ensure pb value is within valid range (0-1)
        if "pb" in values and (
            not isinstance(values["pb"], (int, float))
            or values["pb"] < 0
            or values["pb"] > 1
        ):
            logging.warning(f"Invalid progress bar value: {values['pb']}")
            values["pb"] = default_values["pb"]

        return values

    except Exception as e:
        logging.error(f"Error loading timer values: {e}")
        return default_values


def main(page: ft.Page, t_settings_filename: str):
    """Main application function."""
    page.title = "Timer"

    def adjust_widths(e):
        """Adjust UI elements based on window size."""
        try:
            relative_size = page.window_width / original_width
            # Adjust Text and ProgressBar width
            l_total_time.size = int(15 * relative_size)  # Adjust the width of the Text
            pb.width = int(210 * relative_size)  # Adjust the width of the ProgressBar
            pb.height = int(4 * relative_size)  # Adjust the height
            # Scale Text size
            t_info.size = int(20 * relative_size)
            t_currenttime.size = int(50 * relative_size)
            page.update()
        except Exception as e:
            logging.error(f"Error adjusting widths: {e}")

    # Configure window
    try:
        page.window_frameless = True
        page.window_width = screen_width
        page.window_height = screen_height
        page.on_resize = adjust_widths
    except Exception as e:
        logging.error(f"Error configuring window: {e}")

    # Build UI
    try:
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
    except Exception as e:
        logging.error(f"Error building UI: {e}")
        # Add a fallback UI
        page.add(ft.Text("Error loading timer UI. Check logs."))
        page.update()

    # Monitor timer
    last_update_time = time.time()
    max_retries = 3
    retry_count = 0

    while True:
        try:
            # Check if settings file exists and timer is running
            if not os.path.isfile(t_settings_filename):
                logging.info("Settings file not found. Exiting.")
                break

            values = load_timer_values(t_settings_filename)
            if "timer_running" not in values:
                logging.info("Timer status not found. Exiting.")
                break

            if not values.get("timer_running", False):
                logging.info("Timer not running. Exiting.")
                break

            # Update UI elements
            l_total_time.value = values.get("l_total_time", "--:--")
            pb.value = values.get("pb", 1)
            t_info.value = values.get("t_info", "")
            t_currenttime.value = values.get("t_currenttime", "--:--")
            page.update()
            # wait 5 sec before closing the window
            if t_currenttime.value == "00:00":
                time.sleep(5)
            retry_count = 0  # Reset retry count on successful update

            # Dynamic sleep to maintain update interval
            elapsed = time.time() - last_update_time
            sleep_time = max(0.1, update_interval - elapsed)
            time.sleep(sleep_time)
            last_update_time = time.time()

        except Exception as e:
            logging.error(f"Error updating timer: {e}")
            retry_count += 1

            if retry_count >= max_retries:
                logging.error(f"Max retries ({max_retries}) reached. Exiting.")
                break

            time.sleep(1)  # Short delay before retrying

    # Clean exit
    try:
        page.window_destroy()
    except Exception as e:
        logging.error(f"Error destroying window: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 gui_timer_fullscreen.py <settings_filename>")
        sys.exit(1)

    t_settings_filename = sys.argv[1]
    try:
        ft.app(target=lambda page: main(page, t_settings_filename))
    except Exception as e:
        logging.critical(f"Fatal error running application: {e}")
