#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Set change the color of random pixels
################################################################################
import random
import time
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import hex_to_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def set_pixels():
    wait_for_screen(screen)
    while screen.is_on:
        x, y = random.randint(0, screen.resolution.width - 1), random.randint(0, screen.resolution.height - 1)
        screen.set_pixel(x, y, hex_to_rgb("#ffffff")).accept_frame()
        print(f"Pixel {(x, y)} set to #ffffff")
        time.sleep(1/screen.refresh_rate)

################################################################################
# Run screen commands in a separate thread
Thread(target=set_pixels, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
