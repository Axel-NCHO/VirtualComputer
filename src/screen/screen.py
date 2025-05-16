################################################################################

from fractions import Fraction
from typing import Optional
from pygame.time import Clock

import icontract
import pygame as pg
import numpy as np
from pygame import Surface

################################################################################
class Resolution:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def __getattr__(self, item):
        if item == "ratio":
            ratio = Fraction(self.width, self.height).limit_denominator(100)
            return f"{ratio.numerator}:{ratio.denominator}"
        else:
            raise AttributeError(f'"{self.__class__}" object has no attribute "{item}"')
################################################################################
class Screen:

    _INSIDE = 0  # 0000
    _LEFT = 1  # 0001
    _RIGHT = 2  # 0010
    _BOTTOM = 4  # 0100
    _TOP = 8  # 1000

    #--------------------------------------------------------------------------------
    def __init__(self, height, width, hz: int = 60):
        self.resolution: Resolution = Resolution(width, height)
        self.frame_buffer = np.zeros((width, height, 3), dtype=np.uint8)
        self.is_on = False
        self.refresh_rate = hz
        pg.init()
        self.screen: Optional[Surface] = None
        self.clock: Clock = pg.time.Clock()



    #--------------------------------------------------------------------------------
    def power_on(self):
        self.screen = pg.display.set_mode((self.resolution.width, self.resolution.height), pg.DOUBLEBUF|pg.HWSURFACE,
                                          vsync=1)
        pg.display.set_caption("Virtual screen")
        self.is_on = True
        self.update()

        self._run_event_loop()

    # --------------------------------------------------------------------------------
    @icontract.require(lambda self: self.screen)
    def _run_event_loop(self):
        while self.is_on:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.power_off()
                    break

            if not self.is_on:
                break

            self.update()
            self.clock.tick(self.refresh_rate)

    #--------------------------------------------------------------------------------
    @icontract.ensure(lambda self: not self.is_on)
    def power_off(self):
        self.is_on = False
        pg.quit()

    # --------------------------------------------------------------------------------
    @icontract.require(lambda self: self.screen)
    @icontract.ensure(lambda self: self.screen)
    def update(self):
        if self.is_on:
            surface = pg.surfarray.make_surface(self.frame_buffer)
            self.screen.blit(surface, (0, 0))
            pg.display.flip()

            if pg.time.get_ticks() % 1000 < 16:  # ~once per second
                print(f"FPS: {self.clock.get_fps():.1f}")

    # --------------------------------------------------------------------------------
    @icontract.require(lambda x, y, self: 0 <= x <= self.resolution.width and 0 <= y <= self.resolution.height)
    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        self.frame_buffer[x, y] = color

    # --------------------------------------------------------------------------------
    def fill(self, color: tuple[int, int, int]):
        self.frame_buffer[:, :] = color

    # --------------------------------------------------------------------------------
    @icontract.ensure(lambda hz, self: self.refresh_rate == hz)
    def set_refresh_rate(self, hz: int):
        self.refresh_rate = hz

    # --------------------------------------------------------------------------------
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int]):
        """Draw a line pixel by pixel using Bresenham's line algorithm"""
        clipped = self._cohen_sutherland_clip(x1, y1, x2, y2, self.resolution.width, self.resolution.height)
        if clipped is None:
            return  # Line completely outside

        x1, y1, x2, y2 = clipped
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1

        sx = 1 if x2 > x1 else -1
        sy = 1 if y2 > y1 else -1

        if dx > dy:
            err = dx // 2
            while x != x2:
                self.set_pixel(x, y, color)
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy // 2
            while y != y2:
                self.set_pixel(x, y, color)
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

        self.set_pixel(x, y, color)  # Draw final point

    # --------------------------------------------------------------------------------
    def draw_rectangle(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int], fill: bool = False):
        # Bounds checking
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            return

        # Clip start and end coordinates
        x_start = max(0, x)
        y_start = max(0, y)
        x_end = min(self.resolution.width, x + width)
        y_end = min(self.resolution.height, y + height)

        if fill:
            for yi in range(y_start, y_end):
                for xi in range(x_start, x_end):
                    self.set_pixel(xi, yi, color)
        else:
            self.draw_line(x, y, x + width - 1, y, color)  # Top
            self.draw_line(x, y + height - 1, x + width - 1, y + height - 1, color)  # Bottom
            self.draw_line(x, y, x, y + height - 1, color)  # Left
            self.draw_line(x + width - 1, y, x + width - 1, y + height - 1, color)  # Right

    # --------------------------------------------------------------------------------
    def _compute_out_code(self, x, y, width, height):
        code = self._INSIDE
        if x < 0:
            code |= self._LEFT
        elif x >= width:
            code |= self._RIGHT
        if y < 0:
            code |= self._TOP
        elif y >= height:
            code |= self._BOTTOM
        return code

    # --------------------------------------------------------------------------------
    def _cohen_sutherland_clip(self, x1, y1, x2, y2, width, height):
        out_code1 = self._compute_out_code(x1, y1, width, height)
        out_code2 = self._compute_out_code(x2, y2, width, height)

        while True:
            if not (out_code1 | out_code2):
                # Both points inside
                return x1, y1, x2, y2
            elif out_code1 & out_code2:
                # Line is completely outside
                return None
            else:
                # At least one point is outside
                if out_code1:
                    out_code_out = out_code1
                    x, y = x1, y1
                else:
                    out_code_out = out_code2
                    x, y = x2, y2

                x_new, y_new = 0, 0
                if out_code_out & self._TOP:
                    x_new = x + (x2 - x1) * (0 - y) / (y2 - y1)
                    y_new = 0
                elif out_code_out & self._BOTTOM:
                    x_new = x + (x2 - x1) * (height - 1 - y) / (y2 - y1)
                    y_new = height - 1
                elif out_code_out & self._RIGHT:
                    y_new = y + (y2 - y1) * (width - 1 - x) / (x2 - x1)
                    x_new = width - 1
                elif out_code_out & self._LEFT:
                    y_new = y + (y2 - y1) * (0 - x) / (x2 - x1)
                    x_new = 0

                if out_code_out == out_code1:
                    x1, y1 = int(round(x_new)), int(round(y_new))
                    out_code1 = self._compute_out_code(x1, y1, width, height)
                else:
                    x2, y2 = int(round(x_new)), int(round(y_new))
                    out_code2 = self._compute_out_code(x2, y2, width, height)