#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Draw quadratic Bézier curves at random places
################################################################################
import random
import time
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import  random_color_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def draw_quadratic_bezier():
    wait_for_screen(screen)
    while screen.is_on:
        p0x, p0y, p1x, p1y, p2x, p2y = (random.randint(0, screen.resolution.width),
                                        random.randint(0, screen.resolution.height),
                                        random.randint(0, screen.resolution.width),
                                        random.randint(0, screen.resolution.height),
                                        random.randint(0, screen.resolution.width),
                                        random.randint(0, screen.resolution.height))
        screen.draw_quadratic_bezier(p0x, p0y, p1x, p1y, p2x, p2y, random_color_rgb()).accept_frame()
        print(f"Drew a quadratic bezier curve with P0 {p0x, p0y} with P1 {p1x, p1y} with P2 {p2x, p2y}")
        time.sleep(5)

################################################################################
# Run screen commands in a separate thread
Thread(target=draw_quadratic_bezier, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
