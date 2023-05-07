import time
import flet as ft
import main


def gui(page: ft.Page):
    page.title = "IconButton with `click` event"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_always_on_top = True
    page.window_width = 200
    page.window_height = 200

    def button_clicked(e):
        b.data += 1
        #t.value = f"Button clicked {b.data} time(s)"
        b.disabled = True
        t.value = "working... do not interrupt!"
        b.update()
        try:
            # ... YOUR CODE HERE ... #
            main.main()
            t.value = "Done"
        except Exception as e:
            # ... PRINT THE ERROR MESSAGE ... #
            t.value = e
        b.disabled = False
        b.update()
        t.update()

    b = ft.IconButton(
        icon=ft.icons.PLAY_CIRCLE_FILL_OUTLINED,icon_size=40, on_click=button_clicked, data=0
    )
    t = ft.Text()

    page.add(ft.Container(b))
    page.add(ft.Container(t))

ft.app(target=gui)