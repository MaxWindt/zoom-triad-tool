import time
import PySimpleGUI as sg
import pyautogui
import pygame
import pywinauto
import pyperclip

def send_keys_fast(value):
    prev_value = pyperclip.paste()
    pyperclip.copy(value)
    pywinauto.keyboard.send_keys("^a^v")
    pyperclip.copy(prev_value)

def click_input_no_movement(element):
    pos = pyautogui.position()
    element.click_input()
    pyautogui.moveTo(pos)

def send_to_breakouts(text):
    try:
        #initialize the breakout window
        app = pywinauto.Application(backend="uia").connect(
            title_re="Breakout Sessions - Im Gange.*")


        app_wrapper = app.window(
                title_re="Breakout Sessions - Im Gange.*").wrapper_object()

        app_buttons = app_wrapper.descendants(control_type="Button")
        sending_text_btn = app_buttons[-2]
        sending_text_btn.click() 

        app_menu = app_wrapper.descendants(control_type="MenuItem")
        send_text_menu  = app_menu[0]
        send_voice_menu = app_menu[1]
            
        click_input_no_movement(send_text_menu)
        send_keys_fast(text)
        pywinauto.keyboard.send_keys("{ENTER}")
    except:
        print("Text was not sent")

def make_a_sound():
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound("zimbeln.mp3")
    sound.set_volume(0.5)   # Now plays at 50% of full volume.
    sound.play()  

def main():
    # create the PySimpleGUI window
    layout = [
        [sg.Text("Number of persons:"), sg.InputText(key="-ROUNDS-", default_text="3", size=(5,1))],
            [sg.Text("CheckIn duration (min)"), sg.InputText(key="-CHECKIN-", default_text="2", size=(5,1))],
        [sg.Text("Time per person (min):"), sg.InputText(key="-DURATION-", default_text="1", size=(5,1))],
        [sg.Checkbox("Use Total Time", key="-USE_TOTAL-", default=False)],
        [sg.Text("Total (minutes):"), sg.InputText(key="-TOTALDURATION-", default_text="5", size=(5,1))],
        [sg.Checkbox("Send Text Prompt To Breakouts", key="-SEND_TO_BREAKOUTS-", default=True)],
        [sg.Button("Start Timer"), sg.Button("Stop Timer", disabled=True)],
        [sg.Text("Time remaining: ", key="-TEXTOUT-"),sg.Text("00:00", key="-OUTPUT-", font=("Helvetica", 30))]
    ]
    window = sg.Window("Timer GUI", layout)

    # initialize the timer variables
    total_time = 0
    end_time = 0
    timer_running = False  

    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            break
        
        # calculate the total duration based on the user input
        if values["-USE_TOTAL-"]:
            rounds = int(values["-ROUNDS-"])
            total_time = int(values["-TOTALDURATION-"])
            checkin = int(values["-CHECKIN-"])
            checkout = 2
            round_duration = (total_time - checkin - checkout)// rounds
            window["-DURATION-"].update(round_duration)
        else:
            checkin = int(values["-CHECKIN-"])
            checkout = 2
            rounds = int(values["-ROUNDS-"])
            round_duration = int(values["-DURATION-"])
            total_time = (rounds * round_duration + checkin + checkout) * 60
            window["-TOTALDURATION-"].update(str(total_time // 60))
        
        if event == "Start Timer":
            i =0
            # set the durations for the rounds and total time
            total_time = 0
            while i <= (rounds):
                if i == 0:
                    duration = int(values["-CHECKIN-"])
                    window["-TEXTOUT-"].update(f"Check in")
                elif i == 1:
                    duration = round_duration
                    window["-TEXTOUT-"].update(f"{i}. person")
                else:
                    duration = round_duration
                    window["-TEXTOUT-"].update(f"{i}. person")
                    make_a_sound()
                    if values["-SEND_TO_BREAKOUTS-"]:
                        send_to_breakouts(str(i)+"st person can start now ∞ "+str(i)+". Person kann jetzt beginnen")
                i += 1

                
                # countdown loop
                end_time = time.time() + duration * 60
                timer_running = True
                window["Start Timer"].update(disabled=True)
                window["Stop Timer"].update(disabled=False)
                while timer_running and time.time() < end_time:
                
                    remaining_time = end_time - time.time()
                    mins = int(remaining_time // 60)
                    secs = int(remaining_time % 60)
                    window["-OUTPUT-"].update(f"{mins:02d}:{secs:02d}")
                    event, values = window.read(timeout=100)  # check for "Stop Timer" button press
                    if event == "Stop Timer":
                        i = rounds +1
                        timer_running = False
                        total_time = 0
                        window["-OUTPUT-"].update("00:00")
                        window["Start Timer"].update(disabled=False)
                        window["Stop Timer"].update(disabled=True)
                        window["-TEXTOUT-"].update(f"Stopped")
                        break
                else:
                    window["-TEXTOUT-"].update(f"All rounds finished, Fadeout")
                    window["-OUTPUT-"].update("00:00")
            
            
            
            if timer_running:  # timer completed all rounds
                if values["-SEND_TO_BREAKOUTS-"]:
                    send_to_breakouts("Fadeout ∞ Ausklingen")
                make_a_sound()
                time.sleep(4)
                make_a_sound()
                time.sleep(4)
                make_a_sound()
                window["Start Timer"].update(disabled=False)
                window["Stop Timer"].update(disabled=True)
                total_time = 0

            
        elif event == "Stop Timer":
            timer_running = False
            total_time = 0
            window["-OUTPUT-"].update("00:00")
            window["Start Timer"].update(disabled=False)
            window["Stop Timer"].update(disabled=True)
            
    window.close()

if __name__ == "__main__":
    main()
