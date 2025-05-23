import time
import pyautogui
import pygame
import pywinauto
import pyperclip

# app = pywinauto.Application(backend="uia").connect(title_re="Breakout Sessions - Im Gange.*")
# app_wrapper = app.window(title_re="Breakout Sessions - Im Gange.*").print_control_identifiers()

import json


def save_t_values(settings, filename):
    with open(filename, "w") as file:
        json.dump(settings, file)


def load_t_values(filename):
    with open(filename, "r") as file:
        settings = json.load(file)
    return settings


def delete_t_value(tag, filename):
    # Load current settings from file
    with open(filename, "r") as file:
        settings = json.load(file)

    # Remove key from dictionary
    if tag in settings:
        del settings[tag]

    # Save updated settings to file
    with open(filename, "w") as file:
        json.dump(settings, file)


def send_keys_fast(value):
    prev_value = pyperclip.paste()
    pyperclip.copy(value)
    pywinauto.keyboard.send_keys("^a^v")
    # pyperclip.copy(prev_value)


def click_input_no_movement(element):
    pos = pyautogui.position()
    element.click_input()
    pyautogui.moveTo(pos)


def get_breakout_window(state="open"):
    """Finds the breakout window in a given condition
    Args:
    condition: string
        open, idle, or all

    Returns:
    Window object or None
    """

    # initialize the breakout window
    window_title_open = "Breakout Sessions - Im Gange|Breakout rooms - In Progress"
    window_title_idle = (
        "Breakout Sessions - Nicht begonnen|Breakout rooms - Not Started"
    )

    if state == "open":
        window_title = window_title_open
    if state == "idle":
        window_title = window_title_idle
    elif state == "all":
        window_title = window_title_open + "|" + window_title_idle

    try:
        app = pywinauto.Application(backend="uia").connect(title_re=window_title)

        breakout_window = app.window(title_re=window_title).wrapper_object()
    except Exception:
        return None

    return breakout_window


def get_idle_breakout_window():
    # initialize the breakout window

    window_title = "Breakout Sessions - Nicht begonnen|Breakout Rooms - Not Started"
    try:
        app = pywinauto.Application(backend="uia").connect(title_re=window_title)

        app_wrapper = app.window(title_re=window_title).wrapper_object()
    except Exception:
        return None

    return app_wrapper


def send_text_to_zoom(text):
    try:
        # TODO: set app menu and other variables at the beginning. I think this is updated dynamically but fails, when the setup of the variables takes time.
        # initialize the breakout window
        breakout_window = get_breakout_window("open")

        app_buttons = breakout_window.descendants(control_type="Button")

        sending_text_btn = app_buttons[-2]
        sending_text_btn.click()

        print("clicked on sending_text_btn")

        app_menu = breakout_window.descendants(control_type="MenuItem")
        send_text_menu = app_menu[0]
        send_voice_menu = app_menu[1]

        number_of_buttons = len(app_buttons)

        click_input_no_movement(send_text_menu)

        print("clicked on send_text_menu")

        send_keys_fast(text)

        app_buttons = breakout_window.descendants(control_type="Button")

        # check if message window is visible. This will add another button
        if len(app_buttons) == number_of_buttons + 1:
            app_buttons[0].click()
        else:
            raise ValueError("Message window is not visible")

        return True
    except:
        print("Text was not sent")

        return False


def make_a_sound():
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound("zimbeln.mp3")  # -6db
    sound.set_volume(1)
    sound.play()
    time.sleep(4)


def share_external_audio():
    pywinauto.keyboard.send_keys("%s")
    try:
        app = pywinauto.Application(backend="uia").connect(
            title="Wählen Sie ein Fenster oder eine Anwendung, die Sie freigeben möchten"
        )
        pos = pyautogui.position()
        sharing_window = (
            app.window(
                title="Wählen Sie ein Fenster oder eine Anwendung, die Sie freigeben möchten"
            )
            .ListItem5.set_focus()
            .click_input()
        )
        pyautogui.moveTo(pos)
        # send_keys('{ENTER}')
    except:
        print("no action")


def share_external_audio_stop():
    pywinauto.keyboard.send_keys("%s")


def get_time_left_in_breakouts():

    try:
        # initialize the breakout window
        breakout_window = get_breakout_window("open")

        name = breakout_window._element_info.name

        # Find the position of the opening parenthesis
        parenthesis_index = name.find("(")

        # If opening parenthesis is found
        if parenthesis_index != -1:
            # Split the string based on parentheses
            split_text = name.split("(")

            # Get the second element (which contains the time) and remove the closing parenthesis
            time_string = split_text[1].replace(")", "")
            # Split the time string based on colons
            time_components = time_string.split(":")
        else:
            time_components = "0"
    except:
        time_components = "0"
        print("breakout window is not open")

    return time_components


if __name__ == "__main__":
    what = get_time_left_in_breakouts()
    print(what)
    send_text_to_zoom("what")
    print(get_breakout_window("open"))
    print(get_breakout_window("idle"))
    print(get_breakout_window("all"))
