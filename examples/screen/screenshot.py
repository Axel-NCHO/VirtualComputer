#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Take a screenshot
################################################################################
import os
import time
from pathlib import Path
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import random_color_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def screenshot():
    wait_for_screen(screen)
    if screen.is_on:
        screen.draw_rectangle(100, 100, 300, 100, random_color_rgb()).accept_frame()
        time.sleep(5)
        print("Taking screenshot...")
        dir_ = Path(__file__).parent / "generated"
        os.makedirs(dir_, exist_ok=True)
        screen.export_frame(dir_ / "screenshot.png")
        print(f"Screenshot saved to /src/screen/generated/screenshot.png")

################################################################################
# Run screen commands in a separate thread
Thread(target=screenshot, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
