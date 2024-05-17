# creates tagged breakout groups (AFK, Hosts, Language 1, Language 2)
# preparation: open breakout window with max amount of rooms

import re
import time

import numpy as np
import pyautogui
import util


def find_name(participant_list, name):
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

    # return size of first language to rename rooms accordingly
    size_of_lang1 = len(lang1_split)
    # print(participants_in_groups)
    return hosts, notriad, participants_in_groups, size_of_lang1


def assign_participants_to_room(participants_arr, participant_list_raw, room_id, page):
    empty_seat = 0
    for name in participants_arr:
        if name != "inf" and isinstance(name, str):
            user_id = util.find_participantID(name, participant_list_raw)
            util.web_assign_user_to_breakout_room(page, room_id, user_id)

        else:
            empty_seat = empty_seat + 1
            if group_size - empty_seat < minimal_group:
                break


def breakout_assignment(
    hosts, notriad, participants_in_groups, placeholder_rooms, Breakout_Rooms_Info, page
):
    # main loop
    row = 0
    participant_list_raw = Breakout_Rooms_Info["unassigned"]
    for room in range(
        2 + len(participants_in_groups)
    ):  # specialrooms+participant_rooms
        if room == 0:
            room_id = Breakout_Rooms_Info["rooms"][room]["boId"]
            assign_participants_to_room(hosts, participant_list_raw, room_id, page)
        elif room == 1:
            room_id = Breakout_Rooms_Info["rooms"][room]["boId"]
            assign_participants_to_room(notriad, participant_list_raw, room_id, page)
        else:
            room_id = Breakout_Rooms_Info["rooms"][room + placeholder_rooms]["boId"]
            participant_group = participants_in_groups[row]
            assign_participants_to_room(
                participant_group, participant_list_raw, room_id, page
            )
            row = row + 1

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


def main(settings):
    # Initiate
    st = time.time()
    page = util.start_web_module()
    st_afterInit = time.time()

    Breakout_Rooms_Info = util.web_getBreakoutRooms(page)
    # if no rooms     util.web_remove_all_rooms(page)
    if Breakout_Rooms_Info["rooms"]:
        util.web_remove_all_rooms(page)
        Breakout_Rooms_Info = util.web_getBreakoutRooms(page)

    participant_list = [
        participant["displayName"] for participant in Breakout_Rooms_Info["unassigned"]
    ]

    hosts, notriad, participants_in_groups, size_of_lang1 = create_groups(
        participant_list, settings
    )

    util.create_rooms(page, size_of_lang1, len(participants_in_groups), settings)

    Breakout_Rooms_Info = util.web_getBreakoutRooms(page)

    breakout_assignment(
        hosts,
        notriad,
        participants_in_groups,
        placeholder_rooms,
        Breakout_Rooms_Info,
        page,
    )
    breakout_options = {
        "isAutoJoinRoom": False,
        "isBackToMainSessionEnabled": True,
        "isTimerEnabled": True,
        "timerDuration": 360,
        "notNotifyMe": False,
        "needCountDown": True,
        "waitSeconds": 30,
    }
    util.web_openBreakoutRooms(page, breakout_options)
    # participant_list = np.load("300_participants_coregroup.npy")
    # hosts, notriad, participants_in_rooms = create_groups(participant_list)
    elapsed_time = time.time() - st
    elapsed_time_afterInit = time.time() - st_afterInit
    print(elapsed_time)
    print(elapsed_time_afterInit)
    print(hosts, notriad, participants_in_groups)


if __name__ == "__main__":
    st = time.time()
    page = util.start_web_module()

    Breakout_Rooms_Info = util.web_getBreakoutRooms(page)
    # if no rooms     util.web_remove_all_rooms(page)
    if Breakout_Rooms_Info["rooms"]:
        util.web_remove_all_rooms(page)
        Breakout_Rooms_Info = util.web_getBreakoutRooms(page)

    participant_list = [
        participant["displayName"] for participant in Breakout_Rooms_Info["unassigned"]
    ]
    settings = {
        "group_size": 3,
        "minimal_group": 2,
        "placeholder_rooms": 0,
        "activate_language1": True,
        "activate_language2": True,
        "add_universal_to_language1": True,
        "add_universal_to_language2": True,
        "tags_nt": ["NT"],
        "tags_hosts": ["Host"],
        "tags_lang1": ["DE"],
        "tags_lang2": ["EN"],
    }
    hosts, notriad, participants_in_groups, size_of_lang1 = create_groups(
        participant_list, settings
    )

    util.create_rooms(page, size_of_lang1, len(participants_in_groups), settings)

    Breakout_Rooms_Info = util.web_getBreakoutRooms(page)

    breakout_assignment(
        hosts,
        notriad,
        participants_in_groups,
        placeholder_rooms,
        Breakout_Rooms_Info,
        page,
    )

    breakout_options = {
        "isAutoJoinRoom": False,
        "isBackToMainSessionEnabled": True,
        "isTimerEnabled": True,
        "timerDuration": 360,
        "notNotifyMe": False,
        "needCountDown": True,
        "waitSeconds": 30,
    }
    util.web_openBreakoutRooms(page, breakout_options)
    # participant_list = np.load("300_participants_coregroup.npy")
    # hosts, notriad, participants_in_rooms = create_groups(participant_list)
    et = time.time()
    elapsed_time = et - st
    print(elapsed_time)
    print(hosts, notriad, participants_in_groups)
