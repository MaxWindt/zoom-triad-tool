## checks for changes, marks unwanted groups (NT& smaller then defined group size), 
## creates new groups if not assigned

import pywinauto
import time
import numpy as np
import yaml
from new_groups import create_groups, assign_participants,room_buttons_only, create_new_groups
# get the start time
st = time.time()

def get_settings():
    try:
        with open('settings.txt') as f:
            settings = yaml.safe_load(f)
    except:
        print("Error loading settings, loading defaults")
        settings = {# Version 0.1
                    "group_size" : 3,
                    "minimal_group" : 4,
                    "placeholder_rooms" : 5,
                    "activate_language1" : True,
                    "activate_language2" : True,
                    "add_universal_to_language1" : False,
                    "add_universal_to_language2" : False,
                    "tags_nt":["Triad", "TRIAD", "NT", "triad","tirad","^nt "],
                    "tags_hosts":["Host", ".:.", "Team"],
                    "tags_lang1":["DE", "De-","De ","^de ","^de/","D E "],
                    "tags_lang2":["EN", "En-", "En ", "ES","SP"]}
        with open('settings.txt', 'w') as f:
            yaml.dump(settings, f, sort_keys=False, default_flow_style=False)


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
    toggle_language = [settings["activate_language1"],settings["activate_language2"]]
    add_universal_to_language = [settings["add_universal_to_language1"],settings["add_universal_to_language2"]]
    tags_nt = settings["tags_nt"]
    tags_hosts = settings["tags_hosts"]
    tags_lang1 = settings["tags_lang1"]
    tags_lang2 = settings["tags_lang2"]
    
    return settings

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



# main program

def main():
    
    #initialize the breakout window
    get_settings()
    app = pywinauto.Application(backend="uia").connect(
        title_re="Breakout Sessions - Nicht begonnen")

    breakout_window = app.window(
        title="Breakout Sessions - Nicht begonnen").wrapper_object()
    et1 = time.time()

    assigned = breakout_window.descendants(control_type="TreeItem")
    # variables
    name_list = []
    last_room_nr = -1
    rooms_to_be_cleaned = []
    room_nr = 0


    for i in range(len(assigned)):
        info = assigned[i]._element_info.name
        x = info.split(", ")
        level = [int(s) for s in x[0].split() if s.isdigit()][0]
        name = x[1]

        if level == 0:
            room_nr += 1
            participants_in_room = 0
        else:
            participants_in_room = participants_in_room + 1
            name_list.extend([[room_nr, participants_in_room, x[1]]])
            for y in range(participants_in_room):
                name_list[-y-1][1] = participants_in_room
            # get  [Roomnr, participants_in_room]

    # name_list = [[8, 2, 'NT 9r9j5'], [8, 2, 'NT t8nx9'], [9, 3, '7t774'], [9, 3, 'NT j3fch'], [9, 3, 'q0y23'], [10, 1, 'qynmj'], [11, 3, '46rmz'], [11, 3, '6w57y'], [11, 3, '7y8ex']]
    # name_list = [[ROOM, PARTICIPANTS_SUM, NAME],...]

    name_list_only = []  # = [[NAME],...]
    rooms_to_be_cleaned = []  # = [[ROOM, PARTICIPANTS_SUM],...]
    empty_rooms = []
    for x in range(len(name_list)):
        # create a name-only list
        name_list_only.extend([name_list[x][2]])
        # add single-participant-rooms to no_triad_rooms
        if name_list[x][1] < group_size:  # mark room to be cleaned if room < then group_size
            rooms_to_be_cleaned.extend([[name_list[x][0], name_list[x][1]]])
    #  TODO: check for added names from changes in active breakout.py since new_groups.py
    if name_list_only != []:
        NT_ids = np.flatnonzero(np.chararray.find(name_list_only, "triad") != -1)
        NT_ids = np.append(NT_ids,np.flatnonzero(np.chararray.find(name_list_only, "NT")!= -1))
    else:
        # if all rooms are empty
        create_new_groups()

    last_room = room_nr
    first_empty_room = name_list[-1][0]+1  # last full room + 1
    empty_rooms.extend(range(first_empty_room, last_room))

    if NT_ids.size != 0:
        for x in NT_ids:
            rooms_to_be_cleaned.extend([[name_list[x][0], name_list[x][1]]])
        # no_triad_rooms = no_triad_rooms[(2 < no_triad_rooms)] # remove 1&2 room from rooms to be purged
    else: 
        print("no changes in rooms were found, searching for new participants...") 

    # CLEAN ROOMS
    rooms_to_be_cleaned = np.unique(rooms_to_be_cleaned, axis=0).flatten()
    for x in range(0, len(rooms_to_be_cleaned), 2):
        # put buttons in cache:
        room_buttons = room_buttons_only(breakout_window)  # [1] = room 1
        participant_buttons = breakout_window.descendants(control_type="CheckBox") 

        room_buttons[rooms_to_be_cleaned[x]].click() 
        participant_buttons = breakout_window.descendants(control_type="CheckBox") 
        i=1 
        while i <= rooms_to_be_cleaned[x+1]: 
            participant_buttons[i-1].toggle() 
            i = i + 1 
    # safe empty rooms 
    for room in rooms_to_be_cleaned[::2].tolist():
        if room > 2:
            empty_rooms.insert(0, room) # do not add participants to rooms 1 & 2 

    # fill empty rooms and beyond 
    room_buttons = room_buttons_only(breakout_window) # [1] = room 1 

    room_buttons[empty_rooms[0]].click() 
    participant_list = get_breakout_participants_list(breakout_window) 

    if participant_list != []: 
        hosts, notriad, participants_in_rooms = create_groups(participant_list) 

        for i in range(len(participants_in_rooms)): 
            try: 
                room_buttons[empty_rooms[i]].click() # [1] = room 1 
            except: 
                print("no more free rooms left, please edit manually") 
            participant_ids = participants_in_rooms[i] 
            assign_participants(breakout_window, participant_ids) 

        # assign NT 
        room_buttons[2].click() # [2] = room 2 
        assign_participants(breakout_window, notriad) 

    else: 
        print("no new Participants") 



    # get the end time 
    et = time.time() 
    # get the execution time 
    elapsed_time = et - st 
    print('End:', elapsed_time, 'seconds') 
    # get the execution time 
    elapsed_time = et1 - st 
    print('Execution time 1:', elapsed_time, 'seconds') 
    print()

if __name__ == "__main__":

    main()