################################################################################

import random
import time
from threading import Thread

from screen import Screen
from util.colors import hex_to_rgb, random_color_rgb

################################################################################
screen = Screen(height=720, width=1280)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def wait_for_screen(max_wait_seconds: int = 30):
    wait_for_screen = 0
    while not screen.is_on:
        print("Waiting for the screen to start. Checking again in a second")
        time.sleep(1)
        wait_for_screen += 1
        if wait_for_screen >= max_wait_seconds:
            break

    if wait_for_screen >= max_wait_seconds:
        print(f"The screen hasn't started after {max_wait_seconds} seconds. Exiting.")
    else:
        print(f"The screen has started after {wait_for_screen} seconds.")

# --------------------------------------------------------------------------------
def set_pixels():
    wait_for_screen()
    while screen.is_on:
        x, y = random.randint(0, 700), random.randint(0, 700)
        screen.set_pixel(x, y, hex_to_rgb("#ffffff"))
        print(f"Pixel {(x, y)} set to #ffffff")
        time.sleep(1/screen.refresh_rate)

# --------------------------------------------------------------------------------
def fill_with_colors():
    wait_for_screen()
    start = time.time()
    while screen.is_on:
        x, y = random.randint(0, 700), random.randint(0, 700)
        screen.fill(random_color_rgb())
        time.sleep(1 / screen.refresh_rate)

        # Increment refresh rate every 10 seconds
        if time.time() - start >= 10:
            screen.set_refresh_rate(screen.refresh_rate + 10)
            start = time.time()

# --------------------------------------------------------------------------------
def draw_line():
    wait_for_screen()
    if screen.is_on:
        x1, y1, x2, y2 = (random.randint(0, screen.resolution.width), random.randint(0, screen.resolution.height),
                          random.randint(0, screen.resolution.width), random.randint(0, screen.resolution.height))
        screen.draw_line(x1, y1, x2, y2, random_color_rgb())
        print(f"Drew line from {x1, y1} to {x2, y2}")
        time.sleep(1 / screen.refresh_rate)

# --------------------------------------------------------------------------------
def draw_rectangles():
    wait_for_screen()
    while screen.is_on:
        x, y, width, height = (random.randint(0, screen.resolution.width),
                                 random.randint(0, screen.resolution.height),
                                 200, 150)
        filled = False if random.randint(0, 1) < 0.5 else True
        screen.draw_rectangle(x, y, width, height, random_color_rgb(), fill=filled)
        print(f"Drew rectangle from {x, y} with width {width} and height {height} {"not" if not filled else ""} filled")
        time.sleep(5)


Thread(target=draw_rectangles, daemon=True).start()

screen.power_on()

print("Shutdown")
