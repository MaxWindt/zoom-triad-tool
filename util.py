import pyautogui
import pygame
import pywinauto
import pyperclip

# app = pywinauto.Application(backend="uia").connect(title_re="Breakout Sessions - Im Gange.*")
# app_wrapper = app.window(title_re="Breakout Sessions - Im Gange.*").print_control_identifiers()


def send_keys_fast(value):
    prev_value = pyperclip.paste()
    pyperclip.copy(value)
    pywinauto.keyboard.send_keys("^a^v")
    # pyperclip.copy(prev_value)


def click_input_no_movement(element):
    pos = pyautogui.position()
    element.click_input()
    pyautogui.moveTo(pos)


def send_text_to_zoom(text):
    try:
        # initialize the breakout window
        app = pywinauto.Application(backend="uia").connect(
            title_re="Breakout Sessions - Im Gange.*")

        app_wrapper = app.window(
            title_re="Breakout Sessions - Im Gange.*").wrapper_object()
        name = app_wrapper._element_info.name
        app_buttons = app_wrapper.descendants(control_type="Button")
        sending_text_btn = app_buttons[-2]
        sending_text_btn.click()

        app_menu = app_wrapper.descendants(control_type="MenuItem")
        send_text_menu = app_menu[0]
        send_voice_menu = app_menu[1]

        click_input_no_movement(send_text_menu)

        send_keys_fast(text)

        app_buttons = app_wrapper.descendants(control_type="Button")

        # check if message window is visible. This will add another button
        if len(app_buttons) == 7:
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
    sound.set_volume(0.5)   # Now plays at 50% of full volume.
    sound.play()


def share_external_audio():
    pywinauto.keyboard.send_keys("%s")
    try:
        app = pywinauto.Application(backend="uia").connect(
            title="Wählen Sie ein Fenster oder eine Anwendung, die Sie freigeben möchten")
        pos = pyautogui.position()
        sharing_window = app.window(
            title="Wählen Sie ein Fenster oder eine Anwendung, die Sie freigeben möchten").ListItem5.set_focus().click_input()
        pyautogui.moveTo(pos)
        # send_keys('{ENTER}')
    except:
        print("no action")


def share_external_audio_stop():
    pywinauto.keyboard.send_keys("%s")


def get_time_left_in_breakouts():

    try:
        # initialize the breakout window
        app = pywinauto.Application(backend="uia").connect(
            title_re="Breakout Sessions - Im Gange.*")

        app_wrapper = app.window(
            title_re="Breakout Sessions - Im Gange.*").wrapper_object()
        name = app_wrapper._element_info.name

        # Find the position of the opening parenthesis
        parenthesis_index = name.find('(')

        # If opening parenthesis is found
        if parenthesis_index != -1:
            # Split the string based on parentheses
            split_text = name.split('(')

            # Get the second element (which contains the time) and remove the closing parenthesis
            time_string = split_text[1].replace(')', '')
            # Split the time string based on colons
            time_components = time_string.split(':')
        else:
            time_components = "0"
    except:
        time_components = "0"
        print("breakout window is not open")

    return time_components


if __name__ == '__main__':
    what = get_time_left_in_breakouts()
    print(what)
    send_text_to_zoom("what")
