#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Display typed characters on screen
################################################################################
import time
from pathlib import Path
from threading import Thread

import pygame as pg

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import hex_to_rgb

################################################################################
screen: Screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def typing():
    wait_for_screen(screen)

    # Pre-render font for better performance
    font_path = f"{Path(__file__).parent.parent}/resource/font/Urbanist/static/Urbanist-Thin.ttf"
    font = pg.font.Font(font_path, 15)
    write_pos = [10, 10]
    while screen.is_on:
        char = screen.input_devices["keyboard"].read()
        if char:
            print(f"You pressed {char}")
            screen.draw_text(f"{char}", write_pos[0], write_pos[1], hex_to_rgb("#ffffff"), font=font,
                             next_write_position=write_pos).accept_frame()
        time.sleep(1/60)

################################################################################
# Run screen commands in a separate thread
Thread(target=typing, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
