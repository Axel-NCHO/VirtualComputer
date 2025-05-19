#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Draw text at random places
################################################################################
import random
import pygame as pg
import time
from pathlib import Path
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import  random_color_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def draw_text():
    wait_for_screen(screen)
    while screen.is_on:
        x, y = (random.randint(0, screen.resolution.width),
                random.randint(0, screen.resolution.height))
        with_bg_color = False if random.randint(0, 1) < 0.5 else True
        font_path = f"{Path(__file__).parent.parent.parent}/resource/font/Urbanist/static/Urbanist-Regular.ttf"

        # Pre-render font for better performance
        font = pg.font.Font(font_path, 48)
        text = "Here is some \nmultiline text"
        screen.draw_text(text, x, y,
                         color=random_color_rgb(),
                         font=font,
                         line_spacing=1,
                         bg_color=random_color_rgb() if with_bg_color else None).accept_frame()
        print(f"Drew text {text} with font {font}")
        time.sleep(5)

################################################################################
# Run screen commands in a separate thread
Thread(target=draw_text, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
