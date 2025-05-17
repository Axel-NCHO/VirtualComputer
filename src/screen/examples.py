#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Examples of how do draw on the screen and make animations
################################################################################
import random
import pygame as pg
import time
from pathlib import Path
from threading import Thread

from screen import Screen
from util.colors import hex_to_rgb, random_color_rgb

################################################################################
screen = Screen(height=720, width=1280, hz=1, brightness=1)
print(f"The screen has a ratio of {screen.resolution.ratio}")

# --------------------------------------------------------------------------------
def wait_for_screen(max_wait_seconds: int = 30):
    waited = 0
    while not screen.is_on:
        print("Waiting for the screen to start. Checking again in a second")
        time.sleep(1)
        waited += 1
        if waited >= max_wait_seconds:
            break

    if waited >= max_wait_seconds:
        print(f"The screen hasn't started after {max_wait_seconds} seconds. Exiting.")
    else:
        print(f"The screen has started after {waited} seconds.")

# --------------------------------------------------------------------------------
def set_pixels():
    wait_for_screen()
    while screen.is_on:
        x, y = random.randint(0, 700), random.randint(0, 700)
        screen.set_pixel(x, y, hex_to_rgb("#ffffff"))
        print(f"Pixel {(x, y)} set to #ffffff")
        time.sleep(1/screen.refresh_rate)

# --------------------------------------------------------------------------------
def fill_with_colors():
    wait_for_screen()
    start = time.time()
    while screen.is_on:
        screen.fill(random_color_rgb())
        time.sleep(1 / screen.refresh_rate)

        # Increment refresh rate every 10 seconds
        if time.time() - start >= 10:
            screen.set_refresh_rate(screen.refresh_rate + 10)
            start = time.time()

# --------------------------------------------------------------------------------
def draw_line():
    wait_for_screen()
    if screen.is_on:
        x1, y1, x2, y2 = (random.randint(0, screen.resolution.width), random.randint(0, screen.resolution.height),
                          random.randint(0, screen.resolution.width), random.randint(0, screen.resolution.height))
        screen.draw_line(x1, y1, x2, y2, random_color_rgb())
        print(f"Drew line from {x1, y1} to {x2, y2}")
        time.sleep(1 / screen.refresh_rate)

# --------------------------------------------------------------------------------
def draw_rectangles():
    wait_for_screen()
    while screen.is_on:
        x, y, width, height = (random.randint(0, screen.resolution.width),
                                 random.randint(0, screen.resolution.height),
                                 200, 150)
        filled = False if random.randint(0, 1) < 0.5 else True
        screen.draw_rectangle(x, y, width, height, random_color_rgb(), fill=filled)
        print(f"Drew rectangle from {x, y} with width {width} and height {height} {"not" if not filled else ""} filled")
        time.sleep(5)

# --------------------------------------------------------------------------------
def draw_arcs():
    wait_for_screen()
    while screen.is_on:
        x, y, radius, start, end = (random.randint(0, screen.resolution.width),
                                    random.randint(0, screen.resolution.height),
                                    100,
                                    random.randint(0, 10),
                                    random.randint(20, 360))
        screen.draw_arc(x, y, radius, start, end, random_color_rgb())
        print(f"Drew an arc with center {x, y} with radius {radius} with angle from {start}° to {end}°")
        time.sleep(5)

# --------------------------------------------------------------------------------
def draw_circles():
    wait_for_screen()
    while screen.is_on:
        x, y, radius = (random.randint(0, screen.resolution.width),
                                    random.randint(0, screen.resolution.height),
                                    100)
        screen.draw_circle(x, y, radius, random_color_rgb(), thickness=-1)
        print(f"Drew a circle with center {x, y} with radius {radius}")
        time.sleep(5)

# --------------------------------------------------------------------------------
def draw_ellipses():
    wait_for_screen()
    while screen.is_on:
        x, y, radius_x, radius_y = (random.randint(0, screen.resolution.width),
                                    random.randint(0, screen.resolution.height),
                                    100,
                                    25)
        screen.draw_ellipse(x, y, radius_x, radius_y, random_color_rgb(), thickness=-1)
        print(f"Drew an ellipse with center {x, y} with radius_x {radius_x} and radius_y {radius_y}")
        time.sleep(5)

# --------------------------------------------------------------------------------
def draw_quadratic_bezier():
    wait_for_screen()
    while screen.is_on:
        p0x, p0y, p1x, p1y, p2x, p2y = (random.randint(0, screen.resolution.width),
                                        random.randint(0, screen.resolution.height),
                                        random.randint(0, screen.resolution.width),
                                        random.randint(0, screen.resolution.height),
                                        random.randint(0, screen.resolution.width),
                                        random.randint(0, screen.resolution.height))
        screen.draw_quadratic_bezier(p0x, p0y, p1x, p1y, p2x, p2y, random_color_rgb())
        print(f"Drew a quadratic bezier curve with P0 {p0x, p0y} with P1 {p1x, p1y} with P2 {p2x, p2y}")
        time.sleep(5)

# --------------------------------------------------------------------------------
def draw_cubic_bezier():
    wait_for_screen()
    while screen.is_on:
        p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y = (random.randint(0, screen.resolution.width),
                                                  random.randint(0, screen.resolution.height),
                                                  random.randint(0, screen.resolution.width),
                                                  random.randint(0, screen.resolution.height),
                                                  random.randint(0, screen.resolution.width),
                                                  random.randint(0, screen.resolution.height),
                                                  random.randint(0, screen.resolution.width),
                                                  random.randint(0, screen.resolution.height))
        screen.draw_cubic_bezier(p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, random_color_rgb())
        print(f"Drew a quadratic bezier curve with P0 {p0x, p0y} with P1 {p1x, p1y} with P2 {p2x, p2y} with P3 {p3x, p3y}")
        time.sleep(5)

# --------------------------------------------------------------------------------
def draw_text():
    wait_for_screen()
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
                         bg_color=random_color_rgb() if with_bg_color else None)
        print(f"Drew text {text} with font {font}")
        time.sleep(5)

# --------------------------------------------------------------------------------
def animation_translate_x():
    wait_for_screen()
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
            screen.draw_text(text, x, y,
                             line_spacing=1,
                             color=hex_to_rgb("#ffffff"),
                             font=font)  # Use pre-rendered font
            # screen.draw_ellipse(x, y, 100, 50, hex_to_rgb("#ffffff"), thickness=-1)
            # screen.draw_circle(x, y, 100, hex_to_rgb("#ffffff"), thickness=-1)
            # screen.draw_arc(x, y, 100, 0, 157, hex_to_rgb("#ffffff"))
            time.sleep(1/60)
            screen.clear()

# --------------------------------------------------------------------------------
def animation_ellipse_radius():
    wait_for_screen()
    while screen.is_on:
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
            screen.draw_ellipse(640, 360, rx, ry, hex_to_rgb("#ffffff"), thickness=-1)
            time.sleep(1/screen.refresh_rate)
            screen.clear()
            # screen.draw_ellipse(x, y, 100, 50, hex_to_rgb("#ffffff"))

################################################################################
# Run screen commands in a separate thread
Thread(target=animation_translate_x, daemon=True).start()

# This is a blocking call
screen.power_on()

print("Shutdown")
