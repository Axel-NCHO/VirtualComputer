#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Animation: ellipse with varying radii
################################################################################
import time
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import hex_to_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def animation_ellipse_radius():
    wait_for_screen(screen)
    if screen.is_on:
        rx, ry = 150, 50
        speedx = 500  # pixels per second
        speedy = 500  # pixels per second
        increase_x = False
        increase_y = True

        # Animation timing
        last_time = time.time()

        while True:
            # Calculate delta time independent of refresh rate
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Update position based on real time
            if increase_x:
                rx += int(speedx * dt)
                if rx >= 150:
                    increase_x = False
            else:
                rx -= int(speedx * dt)
                rx = max (50, rx)
                if rx <= 50:
                    increase_x = True

            # Update position based on real time
            if increase_y:
                ry += int(speedy * dt)
                if ry >= 150:
                    increase_y = False
            else:
                ry -= int(speedy * dt)
                ry = max (50, ry)
                if ry <= 50:
                    increase_y = True

            # Drawing operations
            if not screen.is_on:
                break
            screen.draw_ellipse(640, 360, rx, ry, hex_to_rgb("#ffffff"), thickness=-1).accept_frame()
            time.sleep(1/screen.refresh_rate)
            screen.clear()
            # screen.draw_ellipse(x, y, 100, 50, hex_to_rgb("#ffffff"))

################################################################################
# Run screen commands in a separate thread
Thread(target=animation_ellipse_radius, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
