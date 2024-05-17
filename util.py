from playwright.sync_api import sync_playwright, expect
import time
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
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        locale="en-US",
    )
    page = context.new_page()
    page.goto(
        "file:///C:/Users/Max/Documents/code/zoom-triad-tool-js-web-module/index.html"
    )
    expect(page.get_by_label("Enter Full Screen")).to_be_visible(timeout=10000)

    page.get_by_label("Reclaim Host").click()
    return page


def web_getCurrentUser(page):
    User = page.evaluate(
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


def web_remove_all_rooms(page):
    # click workaround to open Breakout Room Window
    page.evaluate(
        """try {
    var bParticipants = document.querySelector(
      '[aria-label^="Breakout Rooms"]'
    );
    bParticipants.click();
  } catch (error) {
    console.error("Breakout Rooms Window already open", error);
  }"""
    )
    page.get_by_role("button", name="Recreate").click()
    page.get_by_label("Recreate").fill("0")
    page.get_by_text("Assign manually").click()
    page.get_by_role("button", name="Recreate").click()
    page.get_by_role("listitem").locator("div").first.hover()
    page.get_by_role("button", name="Delete").click()
    page.get_by_label("Delete Room 1?").get_by_role("button", name="Delete").press(
        "Enter"
    )
    page.get_by_role("button", name="Close").click()


def web_openBreakoutRooms(page, breakout_options):

    page.evaluate(
        """breakout_options => {
            ZoomMtg.openBreakoutRooms({
            options: breakout_options,
            error: function (error) {
                console.error("Error occurred:", error);
            },
            success: function (success) {
                console.log("Here are the breakouts!", success);
            },
        });
        }
        """,
        breakout_options,
    )


def web_createBreakoutRooms(page, array):

    # print(
    page.evaluate(
        """array => {
            ZoomMtg.createBreakoutRoom({
            data: array,
            pattern: 3,
            error: function (error) {
                console.error("Error occurred:", error);
            },
            success: function (success) {
                console.log("Here are the breakouts!", success);
            },
        });
        }
        """,
        array,
    )

    time.sleep(0.1)


def create_rooms(page, size_of_lang1, size_of_lang2, settings):
    # Initialize an empty list to hold the room names
    rooms = []
    tags_lang1 = settings["tags_lang1"][0]
    tags_lang2 = settings["tags_lang2"][0]
    room_number = 1
    # Add Teamroom
    rooms.append(f"Teamroom")
    room_number += 1
    # Add No Triad Room
    rooms.append(f"No Triad")
    room_number += 1
    # Add the Placeholder rooms
    for _ in range(settings["placeholder_rooms"]):
        rooms.append(f"Room {room_number}")
        room_number += 1

    # Add the Language 1 rooms with the provided DE tag
    for _ in range(size_of_lang1):
        rooms.append(f"Room {room_number} {tags_lang1}")
        room_number += 1

    # Add the Language 2 rooms with the provided EN tag
    for _ in range(size_of_lang2):
        rooms.append(f"Room {room_number} {tags_lang2}")
        room_number += 1

    # Add the final 10 rooms without any tags
    for _ in range(100 - room_number):
        rooms.append(f"Room {room_number}")
        room_number += 1

    web_createBreakoutRooms(page, rooms)
    return rooms


def web_assign_user_to_breakout_room(
    page, target_room_id, user_id, success_callback=None, error_callback=None
):
    return page.evaluate(
        """([targetRoomId, userId]) => {
            ZoomMtg.assignUserToBreakoutRoom({
                targetRoomId: targetRoomId,
                userId: userId,
                error: (error) => {
                    console.error("Error occurred:", error);
                    
                },
                success: (success) => {
                    console.log("Here are the breakouts!", success);
                },
            });
        }""",
        [target_room_id, user_id],
    )


def web_getBreakoutRooms(page):
    time.sleep(0.5)  # wait to make sure SDK is ready
    Attendees = page.evaluate(
        """() => {
            return new Promise((resolve) => {
                ZoomMtg.getBreakoutRooms({
                    success: function(res) {
                        resolve(res);
                    },
                    error: function (error) {
                        console.log(error);
                    },
                });
            });
        }"""
    )
    return Attendees["result"]


def find_participantID(display_name, participant_list):
    for participant in participant_list:
        if participant["displayName"] == display_name:
            return participant["participantId"]
    return None


def filter_participant_list(original_list):
    extracted_list = []
    for item in original_list:
        extracted_item = {
            "displayName": item["displayName"],
            "participantUUID": item["participantUUID"],
            "isCoHost": item["isCoHost"],
            "muted": item["muted"],
        }
        extracted_list.append(extracted_item)
    return extracted_list


def test():
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto("https://playwright.dev/")
    page.screenshot(path="example.png")


if __name__ == "__main__":

    page = start_web_module()
    user = web_getCurrentUser(page)

    Breakout_Rooms = web_getBreakoutRooms(page)
    print(Breakout_Rooms)
