#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
import time

from screen.screen import Screen

################################################################################
def wait_for_screen(screen: Screen, max_wait_seconds: int = 30):
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
