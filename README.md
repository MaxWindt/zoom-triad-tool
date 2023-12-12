# Triad Tool for Zoom

<p align="center">
         <img height="500" src="https://github.com/MaxWindt/zoom-triad-tool/assets/86522026/e45c9504-d6c8-42c9-a368-a488d49aeca4" /> 



## Description

**Zoom Triad Tool** is a utility that facilitates the automatic assignment of conference participants to breakout rooms in Zoom, taking into account specific, predefined parameters. This tool provides a solution to a limitation in Zoom, where automatic assignment lacks customizable parameters. Especially in large conferences with numerous parallel breakout rooms, manual assignment becomes impractical.

The tool simulates manual input into Zoom, so it is essential to have a sufficient number of breakout rooms set up for manual allocation in Zoom. Additionally, the Zoom breakout window must remain open during tool execution. Please note that the tool is designed to work only on Windows.

## Installation

1. Download the [Zoom Triad Tool](https://github.com/MaxWindt/zoom-triad-tool/releases/) from the official releases page.

2. Extract the contents of the downloaded ZIP folder.

3. Run the included batch file in the extracted folder.

4. Initial setup might take couple of minutes, the Tool will start automatically after that.

## Usage

1. After installation, launch the tool.

2. Set the desired parameters using the provided user interface.

3. Ensure that the Zoom breakout window is open.

4. Initiate the tool to automate the assignment of conference participants to breakout rooms.

5. Manually start the breakout rooms in Zoom once the tool completes its task.

6. Use the Timer to send prompts to the participants

## Settings

- **Group Size:** Set the default number of conference participants to be assigned per room.

## Advanced Settings

1. **Assignment based on Username Patterns:**
   - Assign participants to a room if their usernames contain specific character combinations. For example people who don't want to participate (e.g., No Triad, NT, X-)

2. **Language-based Assignment:**
   - Assign participants speaking the same language. Users must include a language identifier (e.g., DE, EN) in their usernames.

3. **Minimum Room Size:**
   - Control how the tool handles a mismatch in the number of participants (smaller or larger room).

4. **Additional Advanced Settings:**
   - Customize the tool's behavior further based on your specific requirements.

## Timer Functions

- The tool provides timer functions for ongoing breakout sessions.
- Set the group size, time per person, total breakout time, and a duration time for the session start.
- Notifications and sound cues are triggered at various points during the session.

## Contact and Support

- For questions or suggestions, contact the developer at [max@thesharingspace.de](mailto:max@thesharingspace.de).
- Show your support for the project by [donating](https://www.paypal.com/paypalme/maxschwindt).



**Note:** Ensure that you review and understand the tool's settings and parameters before usage.
