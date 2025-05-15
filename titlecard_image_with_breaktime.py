import argparse
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageStat
import datetime


def show_image_with_timecode(end_time, image_path):
    def close():
        with open(
            os.path.join(os.path.dirname(__file__), "timecode_label_position.txt"), "w"
        ) as f:
            f.write(f"{timecode_label.winfo_x()},{timecode_label.winfo_y()}\n")
        root.destroy()

    def update_timecode():
        # Calculate the remaining time until the end time
        end_time_obj = datetime.datetime.strptime(end_time, "%H:%M").time()
        current_time_obj = datetime.datetime.now().time()
        if current_time_obj > end_time_obj:
            print("End time has passed. Closing the window...")
            close()
        else:
            remaining_time = datetime.datetime.combine(
                datetime.date.today(), end_time_obj
            ) - datetime.datetime.combine(datetime.date.today(), current_time_obj)

            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            # Update the timecode with the remaining time
            timecode_label.config(text=f"{end_time} CET\n⏳{hours}:{minutes:02d} ")
            timecode_label.after(1000, update_timecode)  # Update every second

    def start_drag(event):
        # Save the position where the drag starts
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def on_drag(event):
        # Calculate new label position
        new_x = timecode_label.winfo_x() + (event.x - drag_data["x"])
        new_y = timecode_label.winfo_y() + (event.y - drag_data["y"])
        timecode_label.place(x=new_x, y=new_y)

    def on_drag_end(event):
        # Schedule the background update for 1 second after drag ends
        update_label_bg(timecode_label.winfo_x(), timecode_label.winfo_y())

    def update_label_bg(x, y):
        # Convert label's screen coordinates to image coordinates
        img_x1 = int((x - x_offset) / image_scale)
        img_y1 = int((y - y_offset) / image_scale)
        img_x2 = int((x - x_offset + timecode_label.winfo_width()) / image_scale)
        img_y2 = int((y - y_offset + timecode_label.winfo_height()) / image_scale)

        # Ensure coordinates are within the bounds of the original image
        img_x1 = max(0, min(img_width, img_x1))
        img_y1 = max(0, min(img_height, img_y1))
        img_x2 = max(0, min(img_width, img_x2))
        img_y2 = max(0, min(img_height, img_y2))

        # Label is inside the image; crop the background
        if img_x2 > img_x1 and img_y2 > img_y1:  # Valid crop area
            # Get the background section from the original image
            cropped_area = original_image.crop((img_x1, img_y1, img_x2, img_y2))

            # Resize the cropped area to match the label size
            label_width = timecode_label.winfo_width()
            label_height = timecode_label.winfo_height()
            if label_width > 0 and label_height > 0:
                cropped_area = cropped_area.resize(
                    (label_width, label_height), Image.LANCZOS
                )

                # Convert to PhotoImage and store it to prevent garbage collection
                photo = ImageTk.PhotoImage(cropped_area)
                timecode_label.photo = (
                    photo  # Store reference to prevent garbage collection
                )

                # Calculate average color for text contrast
                stat = ImageStat.Stat(cropped_area)
                avg_color = tuple(int(c) for c in stat.mean[:3])
                luminance = (
                    0.299 * avg_color[0] + 0.587 * avg_color[1] + 0.114 * avg_color[2]
                ) / 255

                # Update the label
                timecode_label.config(
                    image=photo,
                    compound="center",
                    fg="white" if luminance < 0.5 else "black",
                )

    # Initialize the main window
    root = tk.Tk()
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    root.iconbitmap(icon_path)
    root.title("Titlecard")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: close())

    # Load the image
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    original_image = Image.open(image_path)

    # Maintain the aspect ratio of the image
    img_width, img_height = original_image.size
    ratio = min(screen_width / img_width, screen_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_image)

    # Center the image
    global x_offset, y_offset, image_scale
    x_offset = (screen_width - new_width) // 2
    y_offset = (screen_height - new_height) // 2
    image_scale = ratio

    # Create a canvas for displaying the image
    canvas = tk.Canvas(
        root,
        width=screen_width,
        height=screen_height,
        highlightthickness=0,
        bg="black",
    )
    canvas.pack(fill="both", expand=True)
    canvas.create_image(x_offset, y_offset, anchor="nw", image=bg_image)

    # Create a draggable timecode label
    drag_data = {"x": 0, "y": 0}
    timecode_label = tk.Label(
        root,
        text="",
        font=("Arial", 55, "bold"),
        fg="white",
        bg="white",  # Set initial background to black
        padx=0,
        pady=0,
        borderwidth=0,
        relief="flat",
    )

    try:
        with open(
            os.path.join(os.path.dirname(__file__), "timecode_label_position.txt"), "r"
        ) as f:
            x, y = map(int, f.readline().split(","))
            timecode_label.place(x=x, y=y)
    except (FileNotFoundError, ValueError):
        timecode_label.place(x=50, y=50)

    # Bind drag events to the timecode label
    timecode_label.bind("<ButtonPress-1>", start_drag)
    timecode_label.bind("<B1-Motion>", on_drag)
    timecode_label.bind("<ButtonRelease-1>", on_drag_end)

    # Schedule the initial background update and start timecode updates
    root.after(
        500, lambda: update_label_bg(timecode_label.winfo_x(), timecode_label.winfo_y())
    )
    update_timecode()

    # Start the main loop
    root.mainloop()


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show image with timecode")
    parser.add_argument("end_time", type=str, help="End time in HH:MM format")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    args = parser.parse_args()

    show_image_with_timecode(args.end_time, args.image_path)
