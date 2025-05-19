#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Draw rectangles at random places
################################################################################
import random
import time
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import random_color_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def draw_rectangles():
    wait_for_screen(screen)
    while screen.is_on:
        x, y, width, height = (random.randint(0, screen.resolution.width),
                                 random.randint(0, screen.resolution.height),
                                 200, 150)
        filled = False if random.randint(0, 1) < 0.5 else True
        screen.draw_rectangle(x, y, width, height, random_color_rgb(), fill=filled).accept_frame()
        print(f"Drew rectangle from {x, y} with width {width} and height {height} {"not" if not filled else ""} filled")
        time.sleep(5)

################################################################################
# Run screen commands in a separate thread
Thread(target=draw_rectangles, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
