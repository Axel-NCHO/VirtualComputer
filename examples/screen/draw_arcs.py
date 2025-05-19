#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Draw arcs aat random places
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
def draw_arcs():
    wait_for_screen(screen)
    while screen.is_on:
        x, y, radius, start, end = (random.randint(0, screen.resolution.width),
                                    random.randint(0, screen.resolution.height),
                                    100,
                                    random.randint(0, 10),
                                    random.randint(20, 360))
        screen.draw_arc(x, y, radius, start, end, random_color_rgb()).accept_frame()
        print(f"Drew an arc with center {x, y} with radius {radius} with angle from {start}° to {end}°")
        time.sleep(5)

################################################################################
# Run screen commands in a separate thread
Thread(target=draw_arcs, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
