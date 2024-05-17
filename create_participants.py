from playwright.sync_api import sync_playwright
import time


def create_participants():

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    for _ in range(50):
        page = context.new_page()
        page.goto(
            "file:///C:/Users/Max/Documents/code/zoom-triad-tool-js-web-module/index_component.html"
        )
    time.sleep(600)


if __name__ == "__main__":
    create_participants()
