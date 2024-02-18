# creates tagged breakout groups (AFK, Hosts, Language 1, Language 2)
# preparation: open breakout window with max amount of rooms

import re
import time

import numpy as np
import pyautogui
import pyperclip
import pywinauto
import util
from pywinauto.keyboard import send_keys


def get_breakout_participants_list(breakout_window):
    participant_list = breakout_window.descendants(control_type="ListItem")
    breakout_participants_list = []
    for i in range(len(participant_list)):
        parent = participant_list[i]
        child = parent.children()[0]
        child_child = child.children()[0]
        child_child_child = child_child.children_texts()[0]
        breakout_participants_list.extend([child_child_child])
    return breakout_participants_list


def find_name(participant_list, name):
    id_list = []
    name_list = []
    # find names with tags
    for i in range(len(name)):
        r = re.compile(name[i])
        matches = list(filter(r.findall, participant_list))  # Read Note below
        name_list.extend(matches)
    return np.unique(name_list)


def shuffle(array):
    rnd = np.random.default_rng().permuted(array)
    return rnd


def split_into_groups_of(lst, group_size):
    if lst.size != 0:
        rest = len(lst) % group_size
        empty_seats = group_size - rest if rest != 0 else 0
        round_list = np.concatenate((np.full(empty_seats, np.inf), lst))
        split_list = np.split(round_list, len(round_list) / group_size)
    else:
        split_list = [np.full(group_size, np.inf)]
    return split_list


def create_groups(participant_list, settings):

    global group_size
    global minimal_group
    global placeholder_rooms
    global toggle_language
    global add_universal_to_language
    global tags_nt
    global tags_hosts
    global tags_lang1
    global tags_lang2

    group_size = settings["group_size"]
    minimal_group = settings["minimal_group"]
    placeholder_rooms = settings["placeholder_rooms"]
    language1_active = settings["activate_language1"]
    language2_active = settings["activate_language2"]
    add_universal_to_language = [
        settings["add_universal_to_language1"],
        settings["add_universal_to_language2"],
    ]
    tags_nt = settings["tags_nt"]
    tags_hosts = settings["tags_hosts"]
    tags_lang1 = settings["tags_lang1"]
    tags_lang2 = settings["tags_lang2"]

    notriad = find_name(participant_list, tags_nt)
    hosts = find_name(participant_list, tags_hosts)
    lang1 = find_name(participant_list, tags_lang1)
    lang2 = find_name(participant_list, tags_lang2)

    # filter Universal
    universal = np.intersect1d(lang1, lang2)
    # clean out hosts universal and NTs
    lang1_clean = np.setdiff1d(lang1, np.concatenate((universal, notriad, hosts)))
    lang2_clean = np.setdiff1d(lang2, np.concatenate((universal, notriad, hosts)))

    no_tag = np.setdiff1d(
        participant_list,
        np.concatenate((universal, notriad, hosts, lang1_clean, lang2_clean)),
    )
    notag_uni = np.concatenate((universal, no_tag))
    # distribute universal
    if np.sum(add_universal_to_language) != 0:
        uni_split = np.array_split(
            shuffle(notag_uni), np.sum(add_universal_to_language)
        )

    if add_universal_to_language[0]:
        lang1_final = np.concatenate((lang1_clean, uni_split[0]))
    else:
        lang1_final = lang1_clean

    if add_universal_to_language[1]:
        if np.sum(add_universal_to_language) == 1:
            lang2_final = np.concatenate((lang2_clean, uni_split[0]))
        elif np.sum(add_universal_to_language) == 2:
            lang2_final = np.concatenate((lang2_clean, uni_split[1]))
    else:
        lang2_final = lang2_clean

    # split
    lang1_split = split_into_groups_of(shuffle(lang1_final), group_size)
    lang2_split = split_into_groups_of(shuffle(lang2_final), group_size)
    # use languages according to toggle_language
    participants_in_groups = []
    if language1_active:
        participants_in_groups.extend(lang1_split)
    if language2_active:
        participants_in_groups.extend(lang2_split)

    # print(participants_in_groups)
    return hosts, notriad, participants_in_groups


def send_keys_fast(value):
    prev_value = pyperclip.paste()
    pyperclip.copy(value)
    send_keys("^v")
    pyperclip.copy(prev_value)


def starting_position(breakout_window):
    rect = breakout_window.Raum1Static.parent().rectangle()
    breakout_window.set_focus()
    pywinauto.mouse.click(
        coords=(rect.left + 10, round(rect.top + (rect.bottom - rect.top) / 2))
    )


def rename_room(name):
    send_keys("{TAB}{SPACE}")
    send_keys_fast(name)
    send_keys("{ENTER}{TAB}")


# only room buttons accessable for more security
def room_buttons_only(breakout_window):
    room_buttons = breakout_window.descendants(control_type="Button")  # [1] = room 1
    mark_to_del = []
    for i in range(0, len(room_buttons) - 1):
        name = room_buttons[i]._element_info.name
        if name == "Umbenennen":
            mark_to_del.extend([i, i + 1])  # & next Button "Löschen"
    for i in sorted(mark_to_del, reverse=True):
        del room_buttons[i]
    # add something to index 0 to have same id in id&roomnr
    room_buttons = ["close button disabled"] + room_buttons[1:-2]
    return room_buttons


def assign_participants(breakout_window, participants_arr):
    # start participants list
    # send_keys("{TAB}{TAB}{TAB}{SPACE}")
    participant_list = get_breakout_participants_list(breakout_window)
    participant_buttons = breakout_window.descendants(control_type="CheckBox")
    empty_seat = 0
    for name in participants_arr:
        if name != "inf" and isinstance(name, str):
            id = np.flatnonzero(np.chararray.find(participant_list, name) != -1)
            for x in id:  # if a name is doubled use only first
                participant_buttons[int(x)].toggle()
                break
        else:
            empty_seat = empty_seat + 1
            if group_size - empty_seat < minimal_group:
                break


# return to starting position
# send_keys("{ESC}+{TAB}+{TAB}+{TAB}")


def next_room():
    # focus next room and collaps
    send_keys("{DOWN}{LEFT}")


def update_list_positions(id_array, removed_ids):
    for id in removed_ids:
        if not np.isinf(id):
            filter_arr = (id_array > id).astype(int)
            id_array = id_array - filter_arr
    return id_array


def breakout_assignment(
    hosts, notriad, participants_in_rooms, placeholder_rooms, breakout_window
):
    breakout_buttons = room_buttons_only(breakout_window)  # [1] = room 1

    # main loop
    row = 0
    for room in range(2 + len(participants_in_rooms)):  # specialrooms+participant_rooms
        if room == 0:
            breakout_buttons[room + 1].click()  # [1] = room 1
            # rename_room("Teamroom")
            assign_participants(breakout_window, hosts)
            # notriad = update_list_positions(notriad,hosts)
            # participants_in_rooms = update_list_positions(participants_in_rooms,hosts)
            # next_room()
            # print(str(hosts).encode(sys.stdout.encoding, errors='replace'))

        elif room == 1:
            breakout_buttons[room + 1].click()  # [1] = room 1
            # rename_room("No Triad")
            assign_participants(breakout_window, notriad)
            # participants_in_rooms = update_list_positions(participants_in_rooms,notriad)
            # next_room()
            # print(str(notriad).encode(sys.stdout.encoding, errors='replace'))

        # elif room == 2:
        #     for i in range(placeholder_rooms):
        #         next_room()
        #         print("jump over")
        #     # no clue why it is needed but this is the only way the first room collapses
        #     send_keys("{LEFT}")
        else:
            breakout_buttons[room + placeholder_rooms + 1].click()  # [1] = room 1
            participant_ids = participants_in_rooms[row]
            assign_participants(breakout_window, participant_ids)
            # participants_in_rooms = update_list_positions(participants_in_rooms,participant_ids)
            # print(participant_ids)
            row = row + 1
            # send_keys("{LEFT}")
            # next_room()

    # print(str(participants_in_rooms).encode(sys.stdout.encoding, errors='replace'))


def create_new_rooms(breakout_window):
    if (
        pyautogui.confirm(
            text="Do you want to replace your current breakouts?",
            title="Creating Breakouts",
            buttons=["OK", "Cancel"],
        )
        == "OK"
    ):
        breakout_buttons_2 = breakout_window.descendants(
            control_type="Button"
        )  # [1] = room 1
        breakout_buttons_2[-3].click()
        breakout_buttons_2 = breakout_window.descendants(
            control_type="Button"
        )  # [1] = room 1
        breakout_buttons_2[0].click()
    else:
        exit()


def create_new_groups(settings):
    # Initiate

    if util.get_breakout_window("idle") == None:
        print("Breakout window is not open")
        exit()
    breakout_window = util.get_breakout_window("idle")

    # create_new_rooms(breakout_window)

    # get the start time
    st = time.time()
    # get all buttons
    breakout_buttons = room_buttons_only(breakout_window)  # [1] = room 1
    breakout_buttons[1].click()
    participant_list = get_breakout_participants_list(breakout_window)
    # participant_list = np.load("300_participants_coregroup.npy")
    hosts, notriad, participants_in_rooms = create_groups(participant_list, settings)
    print()
    et1 = time.time()
    # get the start time
    st2 = time.time()
    breakout_assignment(
        hosts, notriad, participants_in_rooms, placeholder_rooms, breakout_window
    )
    # get the end time
    et2 = time.time()
    # get the end time
    et = time.time()

    # get the first execution time
    elapsed_time = et1 - st
    print("Execution time creating groups:", elapsed_time, "seconds")
    # get the first execution time
    elapsed_time = et2 - st2
    print("Execution time assigning:", elapsed_time, "seconds")

    # get complete execution time
    elapsed_time = et - st
    print("End:", elapsed_time, "seconds")
    print()


if __name__ == "__main__":

    create_new_groups(settings="ss")

    # participant_list = np.load("300_participants_coregroup.npy")
    # hosts, notriad, participants_in_rooms = create_groups(participant_list)
    # print(participants_in_rooms)
