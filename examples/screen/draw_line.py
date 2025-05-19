#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Draw a straight line
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
def draw_line():
    wait_for_screen(screen)
    if screen.is_on:
        x1, y1, x2, y2 = (random.randint(0, screen.resolution.width), random.randint(0, screen.resolution.height),
                          random.randint(0, screen.resolution.width), random.randint(0, screen.resolution.height))
        screen.draw_line(x1, y1, x2, y2, random_color_rgb()).accept_frame()
        print(f"Drew line from {x1, y1} to {x2, y2}")
        time.sleep(1 / screen.refresh_rate)

################################################################################
# Run screen commands in a separate thread
Thread(target=draw_line, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
