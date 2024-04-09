import pyautogui
import pygame
import pywinauto
import pyperclip

# app = pywinauto.Application(backend="uia").connect(title_re="Breakout Sessions - Im Gange.*")
# app_wrapper = app.window(title_re="Breakout Sessions - Im Gange.*").print_control_identifiers()

import json

temp_settings_filename = "t_settings.json"


def save_t_values(settings):
    with open(temp_settings_filename, "w") as file:
        json.dump(settings, file)


def load_t_values():
    with open(temp_settings_filename, "r") as file:
        settings = json.load(file)
    return settings


def delete_t_value(settings, tag):
    # Remove key from dictionary
    del settings[tag]

    # Serialize data and write back to file
    with open(temp_settings_filename, "w") as file:
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
    window_title_open = "Breakout Sessions - Im Gange|Breakout Rooms - In Progress"
    window_title_idle = (
        "Breakout Sessions - Nicht begonnen|Breakout Rooms - Not Started"
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
        # initialize the breakout window
        breakout_window = get_breakout_window("open")

        app_buttons = breakout_window.descendants(control_type="Button")

        sending_text_btn = app_buttons[-2]
        sending_text_btn.click()

        app_menu = breakout_window.descendants(control_type="MenuItem")
        send_text_menu = app_menu[0]
        send_voice_menu = app_menu[1]

        number_of_buttons = len(app_buttons)

        click_input_no_movement(send_text_menu)

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
    sound = pygame.mixer.Sound("zimbeln.mp3")
    # sound.set_volume(0.5)   # Now plays at 50% of full volume.
    sound.play()


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


def start_web_module():

    import Browser

    global browser
    browser = Browser.Browser()

    browser.new_browser(headless=False)
    browser.new_page(
        "http://127.0.0.1:9999/meeting.html?name=TG9jYWwzLjUuMldpbjEwI2ZpcmVmb3gvMTI0LjA%3D&mn=3858026425&email=&pwd=1&role=0&lang=en-US&signature=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBLZXkiOiJVVWl3Mm84RkROcVlHRmZEMXh4TkRlMHhDQ25FdFpPb0wyODkiLCJzZGtLZXkiOiJVVWl3Mm84RkROcVlHRmZEMXh4TkRlMHhDQ25FdFpPb0wyODkiLCJpYXQiOjE3MTI2NTc2ODgsImV4cCI6MTcxMjY2NDg4OCwibW4iOjM4NTgwMjY0MjUsInJvbGUiOjB9.A-BRbmfl8fpbL-EBofq90W0GxI7fuCGfMHKejqic2Dg&china=0&sdkKey=UUiw2o8FDNqYGFfD1xxNDe0xCCnEtZOoL289"
    )


def web_getCurrentUser():
    User = browser.evaluate_javascript(
        None,
        """() => {
            return new Promise(resolve => {
                ZoomMtg.getCurrentUser({
                    success: function(res) {
                        resolve(res.result.currentUser);
                    },
                });
            });
            }
            """,
    )
    return User


def web_getUnassignedAttendeeList():
    Attendees = browser.evaluate_javascript(
        None,
        """() => {
            return new Promise(resolve => {
                ZoomMtg.getUnassignedAttendeeList({
                    success: function(res) {
                        resolve(res);
                    },
                });
            });
            }
            """,
    )
    return Attendees


if __name__ == "__main__":
    what = get_time_left_in_breakouts()
    print(what)
    send_text_to_zoom("what")
    print(get_breakout_window("open"))
    print(get_breakout_window("idle"))
    print(get_breakout_window("all"))
