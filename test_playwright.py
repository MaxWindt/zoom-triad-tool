import time
from playwright.sync_api import Playwright, sync_playwright, expect


def run():

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


def add_listener_test(page):
    print("")


def allow_unmute(page):
    try:
        # Execute the JavaScript code to click on the element
        page.evaluate(
            """
        document.querySelector(
          '[aria-label^="open the participants list pane"]'
        ).click();
        """
        )
    except Exception as error:
        print("Participants Window already open", error)
    try:
        expect(page.get_by_label("More managing participants")).to_be_visible()
        page.evaluate(
            """
            document.querySelector(
            "[id='particioantHostDropdown']"
            ).click();
        """
        )
    except Exception as error:
        print("CoHost Rights are not given", error)

    try:
        expect(
            page.get_by_label("Allow participants to unmute themselves unselect")
        ).to_be_visible()
        page.get_by_label("Allow participants to unmute themselves unselect").click()
        print("successfully allowed unmuting")
    except Exception as error:
        print("Unmuting already allowed", error)


def disallow_unmute(page):
    try:
        # Execute the JavaScript code to click on the element
        page.evaluate(
            """
        document.querySelector(
          '[aria-label^="open the participants list pane"]'
        ).click();
        """
        )
    except Exception as error:
        print("Participants Window already open", error)

    try:
        expect(page.get_by_label("More managing participants")).to_be_visible()
        page.evaluate(
            """
            document.querySelector(
            "[id='particioantHostDropdown']"
            ).click();
        """
        )
    except Exception as error:
        print("CoHost Rights are not given", error)

    try:
        expect(
            page.get_by_label("Allow participants to unmute themselves unselect")
        ).to_be_visible()
        page.get_by_label("Allow participants to unmute themselves unselect").click()
        print("successfully allowed unmuting")

        # TODO:remove listener onActiveSpeaker
    except Exception as error:
        print("Unmuting already disallowed", error)


if __name__ == "__main__":
    page = run()
    import util

    participants = util.web_getBreakoutRooms(page)

    participants = participants["unassigned"]
    filtered_paticipants = util.filter_participant_list(participants)
    print(filtered_paticipants)

    # print(participants["unassigned"][0]["displayName"])
    # print(participants["unassigned"][0]["participantUUID"])

    # print(participants["rooms"][0]["boId"])
    # print(participants["rooms"][0]["participants"][0])
    page.pause()
