#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Fill the screen with random colors
################################################################################
import time
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import random_color_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def fill_with_colors():
    wait_for_screen(screen)
    start = time.time()
    while screen.is_on:
        screen.fill(random_color_rgb()).accept_frame()
        time.sleep(1 / screen.refresh_rate)

        # Increment refresh rate every 10 seconds
        if time.time() - start >= 10:
            screen.set_refresh_rate(screen.refresh_rate + 10)
            start = time.time()

################################################################################
# Run screen commands in a separate thread
Thread(target=fill_with_colors, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
