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
