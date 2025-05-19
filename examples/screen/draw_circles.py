#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Draw circles at random places
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
def draw_circles():
    wait_for_screen(screen)
    while screen.is_on:
        x, y, radius = (random.randint(0, screen.resolution.width),
                                    random.randint(0, screen.resolution.height),
                                    100)
        screen.draw_circle(x, y, radius, random_color_rgb(), thickness=-1).accept_frame()
        print(f"Drew a circle with center {x, y} with radius {radius}")
        time.sleep(5)

################################################################################
# Run screen commands in a separate thread
Thread(target=draw_circles, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
