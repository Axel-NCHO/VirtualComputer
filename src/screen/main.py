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
    while screen.is_on:
        x, y = random.randint(0, 700), random.randint(0, 700)
        screen.fill(random_color_rgb())
        print(f"Screen filled with random color")
        time.sleep(1 / screen.refresh_rate)

Thread(target=fill_with_colors, daemon=True).start()

screen.power_on()

print("Shutdown")
