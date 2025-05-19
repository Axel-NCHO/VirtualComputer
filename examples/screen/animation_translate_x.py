#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Animation: translate objects on the x-axis (width) from left to right
################################################################################
import pygame as pg
import time
from pathlib import Path
from threading import Thread

from examples.util.screen_usage import wait_for_screen
from screen.screen import Screen
from util.colors import hex_to_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=120, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def animation_translate_x():
    wait_for_screen(screen)
    while screen.is_on:
        x, y = 0, 100
        font_path = f"{Path(__file__).parent.parent.parent}/resource/font/Urbanist/static/Urbanist-Regular.ttf"
        text = "Here is some \nmultiline text"
        speed = 500  # pixels per second

        # Pre-render font for better performance
        font = pg.font.Font(font_path, 48)

        # Animation timing
        last_time = time.time()

        while x < screen.resolution.width:
            # Calculate delta time independent of refresh rate
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Update position based on real time
            x += int(speed * dt)
            if x >= screen.resolution.width:
                x = 0  # Reset when off-screen

            # Drawing operations
            if not screen.is_on:
                break
            # screen.draw_text(text, x, y,
            #                  line_spacing=1,
            #                  color=hex_to_rgb("#ffffff"),
            #                  bg_color=hex_to_rgb("#ee45ab"),
            #                  font=font).accept_frame()
            screen.draw_ellipse(x, y, 100, 50, hex_to_rgb("#ffffff"), thickness=-1) \
                  .draw_circle(x, y+200, 100, hex_to_rgb("#ffffff"), thickness=-1) \
                  .draw_rectangle(x, y+400, 100, 100, hex_to_rgb("#ffffff"), fill=True) \
                  .accept_frame()
            # screen.draw_arc(x, y, 100, 0, 157, hex_to_rgb("#ffffff"))
            time.sleep(1/60)
            screen.clear()

################################################################################
# Run screen commands in a separate thread
Thread(target=animation_translate_x, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
