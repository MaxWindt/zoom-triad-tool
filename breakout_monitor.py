import flet as ft
import util


def main(page: ft.Page):
    data_table = ft.DataTable()
    page.window_width = 300
    page.add(
        ft.Row(
            [
                ft.Text(
                    value="Room Monitor ", theme_style=ft.TextThemeStyle.HEADLINE_SMALL
                ),
                ft.Icon(name=ft.icons.MEETING_ROOM),
                ft.Text(" : "),
                ft.Icon(name=ft.icons.GROUP),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )
    page.add(data_table)
    while True:
        # Room Details determine languages for the whole ID and reduce to [Room Nr, Language, Nr of participants]
        try:
            room_details = get_language_of_group(get_active_breakout_list())

            DE = room_details[0]
            EN = room_details[1]

            # Determine the maximum length of the arrays
            max_length = max(len(DE), len(EN))

            # Create DataTable
            data_table.columns = [
                ft.DataColumn(ft.Text("DE Room")),
                ft.DataColumn(ft.Text("EN Room")),
            ]
            data_table.rows = [
                # Populate DataTable with values from DE and EN arrays
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                tooltip="Room : Size",
                                value=str(
                                    "" + DE[i][0] + " - " + DE[i][2] + ""
                                    if i < len(DE)
                                    else ""
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                tooltip="Room : Size",
                                value=str(
                                    "" + EN[i][0] + " - " + EN[i][2] + ""
                                    if i < len(EN)
                                    else ""
                                ),
                            )
                        ),
                    ]
                )
                for i in range(max_length)
            ]
        except:
            print("error reading the breakout window")
        # data_table.update()

        page.update()
        time.sleep(1)


## checks for changes while breakouts are running

import sys
import pywinauto
import numpy as np
import time


# Function to determine languages for the whole ID and reduce to [Room Nr, Language, Nr of participants]
def get_language_of_group(list_of_participants):
    def determine_languages_for_id(id):
        languages_count = {"1": 0, "2": 0}

        for row in list_of_participants[list_of_participants[:, 0] == id]:
            if "DE" in row[2]:
                languages_count["1"] += 1
            elif "EN" in row[2]:
                languages_count["2"] += 1

        # If only one language is present, keep it as is
        if languages_count["1"] == 0:
            return "2"
        elif languages_count["2"] == 0:
            return "1"

        # Sort languages by count in descending order
        sorted_languages = sorted(languages_count.items(), key=lambda x: x[1])

        # Concatenate the languages with the highest count followed by the second highest count
        return sorted_languages[1][0] + sorted_languages[0][0]

    # Add a new column for languages
    languages_column = np.array(
        [determine_languages_for_id(id) for id in list_of_participants[:, 0]]
    )

    # Add the languages column to the original array
    result_array = np.column_stack(
        (list_of_participants[:, :1], languages_column, list_of_participants[:, 1:])
    )

    # Reduce to the first three columns and remove duplicates
    result_array = np.unique(result_array[:, :3], axis=0)

    # put smallest rooms on top
    sorted_data = sorted(result_array, key=lambda x: int(x[2]))
    # filter out full rooms
    filtered_data = [row for row in sorted_data if row[2] != "3"]

    # sorting rooms based on language
    rooms_with_language_1 = []
    rooms_with_language_2 = []
    rooms_with_language_2_containing_1 = []
    rooms_with_language_1_containing_2 = []

    for row in filtered_data:
        if row[1] == "1":
            rooms_with_language_1.append(row)
        elif row[1] == "2":
            rooms_with_language_2.append(row)
        elif row[1] == "21":
            rooms_with_language_2_containing_1.append(row)
        elif row[1] == "12":
            rooms_with_language_1_containing_2.append(row)
    rooms_with_capacity = [
        rooms_with_language_1,
        rooms_with_language_2,
        rooms_with_language_1_containing_2,
        rooms_with_language_2_containing_1,
    ]

    # print("room_with_language_1:", np.array(rooms_with_language_1))
    # print("room_with_language_2:", np.array(rooms_with_language_2))
    # print("room_with_language_2_containing_1:", np.array(rooms_with_language_2_containing_1))
    # print("room_with_language_1_containing_2:", np.array(rooms_with_language_1_containing_2))

    return rooms_with_capacity


def get_active_breakout_list():

    if util.get_breakout_window("all") == None:
        print("Breakout window is not open")
        exit()

    breakout_window = util.get_breakout_window("all")

    tabs = breakout_window.descendants(control_type="TabItem")
    assigned = breakout_window.descendants(control_type="TreeItem")
    room_nr = 0
    name_list = []
    for i in range(len(assigned)):
        info = assigned[i]._element_info.name
        x = info.split(", ")
        try:  # TODO Error List out if range after a while :/ just a quickfix right now
            level = [int(s) for s in x[0].split() if s.isdigit()][0]
        except:
            break
        name = x[1]

        if level == 0:
            room_nr += 1
            participants_in_room = 0
        else:
            participants_in_room = participants_in_room + 1
            name_list.extend([[room_nr, participants_in_room, x[1]]])
            for y in range(participants_in_room):
                name_list[-y - 1][1] = participants_in_room
            # get  [Roomnr, participants_in_room]
    return np.array(name_list)


if __name__ == "__main__":
    # main()
    # name_list = get_active_breakout_list()
    # saved_list = np.load("active_breakouts_coregroup.npy")
    # np.save("active_breakouts_coregroup.npy", name_list)
    # room_details = get_language_of_group(name_list)

    # Run the app with the main function
    ft.app(target=main)
