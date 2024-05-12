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
        if name == "Umbenennen" or name == "Rename":
            mark_to_del.extend([i, i + 1])  # & next Button "Löschen"
    for i in sorted(mark_to_del, reverse=True):
        del room_buttons[i]
    # add something to index 0 to have same id in id&roomnr
    room_buttons = ["close button disabled"] + room_buttons[1:-2]
    return room_buttons


def assign_participants_to_room(participants_arr, participant_list_raw, room_id, page):
    empty_seat = 0
    for name in participants_arr:
        if name != "inf" and isinstance(name, str):
            user_id = util.find_participant_UUID(name, participant_list_raw)
            for x in id:  # if a name is doubled use only first
                util.web_assign_user_to_breakout_room(page, room_id, user_id)
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
    # main loop
    row = 0
    for room in range(2 + len(participants_in_rooms)):  # specialrooms+participant_rooms
        if room == 0:
            room_id = Breakout_Rooms["rooms"][room]["boId"]
            assign_participants_to_room(breakout_window, hosts)
        elif room == 1:
            room_id = Breakout_Rooms["rooms"][room]["boId"]
            assign_participants_to_room(notriad, participant_list_raw, room_id, page)
        else:
            room_id = Breakout_Rooms["rooms"][room + placeholder_rooms]["boId"]
            participant_group = participants_in_rooms[row]
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
    page = util.start_web_module()
    Breakout_Rooms = util.web_getBreakoutRooms(page)

    participant_list_raw = Breakout_Rooms["unassigned"]
    rooms_list = Breakout_Rooms["rooms"]

    participant_list_raw = [
        {
            "participantId": 16778240,
            "displayName": "Max",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": False,
            "isHold": False,
            "persistentID": "BCEE6479-FF74-D64B-6E17-85DDFA2CADD2",
            "participantUUID": "BCEE6479-FF74-D64B-6E17-85DDFA2CADD2",
            "customerKey": "",
        },
        {
            "participantId": 16783360,
            "displayName": "DE - Anna - tafhb",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "52F66BEF-4C6B-5F43-1AF7-1F65BB102D00",
            "participantUUID": "52F66BEF-4C6B-5F43-1AF7-1F65BB102D00",
            "customerKey": "",
        },
        {
            "participantId": 16784384,
            "displayName": "DE - Maria - zrjzt",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "32198124-CC93-0164-F812-A2094BF0BDEE",
            "participantUUID": "32198124-CC93-0164-F812-A2094BF0BDEE",
            "customerKey": "",
        },
        {
            "participantId": 16785408,
            "displayName": "DE/EN - Carlos - 4lrk0",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "95FF50E3-4423-74E6-99A8-4302C124742D",
            "participantUUID": "95FF50E3-4423-74E6-99A8-4302C124742D",
            "customerKey": "",
        },
        {
            "participantId": 16786432,
            "displayName": "DE - Jennifer - f69ky",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "CE91A3B9-5ED7-4F44-0ACA-8D82B03C8171",
            "participantUUID": "CE91A3B9-5ED7-4F44-0ACA-8D82B03C8171",
            "customerKey": "",
        },
        {
            "participantId": 16787456,
            "displayName": "DE/EN - Matthias - kuwu7",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "12516D36-62B9-B66B-57AF-748FC3BDBD5F",
            "participantUUID": "12516D36-62B9-B66B-57AF-748FC3BDBD5F",
            "customerKey": "",
        },
        {
            "participantId": 16788480,
            "displayName": "EN - Sabine - c3yrs",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "C7870EDF-5F49-AF57-BA8D-F35BC354EDBE",
            "participantUUID": "C7870EDF-5F49-AF57-BA8D-F35BC354EDBE",
            "customerKey": "",
        },
        {
            "participantId": 16789504,
            "displayName": "EN - Sarah - ogr2u",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "97EE20F2-EB0A-CE1C-AF4F-ED00EB466DE8",
            "participantUUID": "97EE20F2-EB0A-CE1C-AF4F-ED00EB466DE8",
            "customerKey": "",
        },
        {
            "participantId": 16790528,
            "displayName": "DE/EN - David - g48pd",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "170FEF94-0223-B99F-AF8E-4CFBD190C303",
            "participantUUID": "170FEF94-0223-B99F-AF8E-4CFBD190C303",
            "customerKey": "",
        },
        {
            "participantId": 16791552,
            "displayName": "NT - Javier - ibrrb",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "1E8F819F-475C-A276-85FB-25B2A3963EDF",
            "participantUUID": "1E8F819F-475C-A276-85FB-25B2A3963EDF",
            "customerKey": "",
        },
        {
            "participantId": 16792576,
            "displayName": "EN - Sofía - sjgi1",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "236BE152-901B-9495-EA1E-09D04F28ED6E",
            "participantUUID": "236BE152-901B-9495-EA1E-09D04F28ED6E",
            "customerKey": "",
        },
        {
            "participantId": 16793600,
            "displayName": "EN - Sarah - se4td",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "6D8A8DA0-125B-2D7D-C551-53B32157FA12",
            "participantUUID": "6D8A8DA0-125B-2D7D-C551-53B32157FA12",
            "customerKey": "",
        },
        {
            "participantId": 16794624,
            "displayName": "EN - Carlos - uc2uw",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "8AF86002-9A25-B8BE-2112-71565785EA31",
            "participantUUID": "8AF86002-9A25-B8BE-2112-71565785EA31",
            "customerKey": "",
        },
        {
            "participantId": 16795648,
            "displayName": "DE - Isabella - 9w71e",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "977E8357-E80C-35E0-C158-827F1AAD0CC1",
            "participantUUID": "977E8357-E80C-35E0-C158-827F1AAD0CC1",
            "customerKey": "",
        },
        {
            "participantId": 16796672,
            "displayName": "NT - Antonio - 2imwz",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "F837CF48-7523-BAB9-85AA-AC0561730B8A",
            "participantUUID": "F837CF48-7523-BAB9-85AA-AC0561730B8A",
            "customerKey": "",
        },
        {
            "participantId": 16797696,
            "displayName": "DE/EN - John - ivc4v",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "FF9A4E3D-80F5-F07A-F6C7-D3FF22A25C18",
            "participantUUID": "FF9A4E3D-80F5-F07A-F6C7-D3FF22A25C18",
            "customerKey": "",
        },
        {
            "participantId": 16798720,
            "displayName": "DE/EN - Carmen - n3nyt",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "0A3F94E4-42CF-FA38-01D9-9696BE838D93",
            "participantUUID": "0A3F94E4-42CF-FA38-01D9-9696BE838D93",
            "customerKey": "",
        },
        {
            "participantId": 16799744,
            "displayName": "DE - Jessica - 61qlr",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "A00EA774-DBED-B35C-AF52-9E1A8346F7D5",
            "participantUUID": "A00EA774-DBED-B35C-AF52-9E1A8346F7D5",
            "customerKey": "",
        },
        {
            "participantId": 16800768,
            "displayName": "NT - Ashley - ms71g",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "C8531BB1-8671-B935-F850-109D7039496E",
            "participantUUID": "C8531BB1-8671-B935-F850-109D7039496E",
            "customerKey": "",
        },
        {
            "participantId": 16801792,
            "displayName": "DE - Elena - jv4ca",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "5BA4CDB3-72CC-E53E-C781-F743D493DFE2",
            "participantUUID": "5BA4CDB3-72CC-E53E-C781-F743D493DFE2",
            "customerKey": "",
        },
        {
            "participantId": 16802816,
            "displayName": "DE - Ashley - myybo",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "AAEF3DAA-6DDA-D024-4E2B-AAFA4F5F7372",
            "participantUUID": "AAEF3DAA-6DDA-D024-4E2B-AAFA4F5F7372",
            "customerKey": "",
        },
        {
            "participantId": 16803840,
            "displayName": "DE/EN - Isabella - ug8r4",
            "muted": False,
            "audio": "",
            "isHost": False,
            "isCoHost": "",
            "isGuest": True,
            "isHold": False,
            "persistentID": "AE11CF49-A68B-AADB-DFAB-FC928370E462",
            "participantUUID": "AE11CF49-A68B-AADB-DFAB-FC928370E462",
            "customerKey": "",
        },
    ]
    participant_list = [
        participant["displayName"] for participant in participant_list_raw
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

    hosts, notriad, participants_in_groups = create_groups(participant_list, settings)

    # participant_list = np.load("300_participants_coregroup.npy")
    # hosts, notriad, participants_in_rooms = create_groups(participant_list)
    print(hosts, notriad, participants_in_groups)
