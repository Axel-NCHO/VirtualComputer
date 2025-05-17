################################################################################
import math
from fractions import Fraction
from threading import Lock
from typing import Optional
from pygame.time import Clock

import pygame as pg
import numpy as np
import cv2
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
    def __init__(self, height, width, hz: int = 60, brightness: float = 1.0):
        self.resolution: Resolution = Resolution(width, height)
        self.frame_buffer = np.zeros((width, height, 3), dtype=np.uint8)
        self.is_on = False
        self.refresh_rate = hz
        pg.init()
        self.screen: Optional[Surface] = None
        self.surface = pg.Surface((self.resolution.width, self.resolution.height))
        self.clock: Clock = pg.time.Clock()
        self.brightness: float = brightness
        self.bright_frame = None
        self._dirty = False
        self.cached_texts: dict[tuple[str, bool, tuple[int, int, int], tuple[int, int, int], pg.font.Font], pg.Surface] = {}
        self._dirty_lock = Lock()

    #--------------------------------------------------------------------------------
    def power_on(self):
        self.screen = pg.display.set_mode((self.resolution.width, self.resolution.height),
                                          pg.DOUBLEBUF | pg.HWSURFACE,
                                          vsync=1)
        pg.display.set_caption("Virtual screen")
        self.is_on = True
        self.update()

        self._run_event_loop()

    # --------------------------------------------------------------------------------
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
    def power_off(self):
        self.is_on = False
        pg.quit()

    # --------------------------------------------------------------------------------
    def update(self):
        if self.is_on:
            if self._dirty:
                if self.brightness != 1.0:
                    self.bright_frame = np.clip(self.frame_buffer.astype(np.float16) * self.brightness, 0, 255).astype(np.uint8)
                else:
                    self.bright_frame = self.frame_buffer.copy()
                pg.surfarray.blit_array(self.surface, self.bright_frame)
                with self._dirty_lock:
                    self._dirty = False
            self.screen.blit(self.surface, (0, 0))
            pg.display.flip()

            if pg.time.get_ticks() % 1000 < 16:  # ~once per second
                print(f"FPS: {self.clock.get_fps():.1f}")

    # --------------------------------------------------------------------------------
    def set_brightness(self, brightness: float):
        self.brightness = brightness

    # --------------------------------------------------------------------------------
    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        self.frame_buffer[x, y] = color

    # --------------------------------------------------------------------------------
    def fill(self, color: tuple[int, int, int]):
        self.frame_buffer[:, :] = color

    # --------------------------------------------------------------------------------
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
        with self._dirty_lock:
            self._dirty = True

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
            self.frame_buffer[x_start:x_end, y_start:y_end] = color
        else:
            self.draw_line(x, y, x + width - 1, y, color)  # Top
            self.draw_line(x, y + height - 1, x + width - 1, y + height - 1, color)  # Bottom
            self.draw_line(x, y, x, y + height - 1, color)  # Left
            self.draw_line(x + width - 1, y, x + width - 1, y + height - 1, color)  # Right

        with self._dirty_lock:
            self._dirty = True

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

    def draw_arc(self, cx: int, cy: int, radius: int, angle_start: int, angle_end: int,
                 color: tuple[int, int, int]):
        """Draw an arc by plotting points along a circular path within angle range."""
        if radius <= 0:
            return  # Nothing to draw

        x_max, y_max = self.resolution.width, self.resolution.height

        # Convert degrees to radians
        rad_start = math.radians(angle_start)
        rad_end = math.radians(angle_end)

        # Normalize angle range
        if rad_end < rad_start:
            rad_end += 2 * math.pi  # Support for angles like (330°, 30°)

        steps = max(8 * radius, 1)  # More steps = smoother arc
        delta_angle = (rad_end - rad_start) / steps

        for i in range(steps + 1):
            theta = rad_start + i * delta_angle
            x = int(cx + radius * math.cos(theta))
            y = int(cy + radius * math.sin(theta))

            # Skip out-of-bounds points
            if 0 <= x < x_max and 0 <= y < y_max:
                self.set_pixel(x, y, color)

        with self._dirty_lock:
            self._dirty = True

    # --------------------------------------------------------------------------------
    def draw_circle(self, cx: int, cy: int, radius: int, color: tuple[int, int, int], fill: bool = False):
        if not fill:
            self.draw_arc(cx, cy, radius, 0, 360, color)
        else:
            # x_max, y_max = self.resolution.width, self.resolution.height
            #
            # for y in range(-radius, radius + 1):
            #     y_pos = cy + y
            #     if y_pos < 0 or y_pos >= y_max:
            #         continue
            #
            #     x_span = int((radius ** 2 - y ** 2) ** 0.5)
            #     x_start = cx - x_span
            #     x_end = cx + x_span
            #
            #     # Clip horizontal bounds
            #     x_start = max(x_start, 0)
            #     x_end = min(x_end, x_max - 1)
            #
            #     for x in range(x_start, x_end + 1):
            #         self.set_pixel(x, y_pos, color)
            cv2.circle(self.frame_buffer, (cy, cx), radius, color, -1)

            with self._dirty_lock:
                self._dirty = True

    # --------------------------------------------------------------------------------
    def draw_ellipse(self, cx: int, cy: int, rx: int, ry: int, color: tuple[int, int, int], thickness: int = 1):
        """Draw an outlined ellipse using polar coordinates"""
        # if rx <= 0 or ry <= 0:
        #     return
        #
        # steps = max(8 * max(rx, ry), 1)
        # for i in range(steps):
        #     angle = 2 * math.pi * i / steps
        #     x = int(cx + rx * math.cos(angle))
        #     y = int(cy + ry * math.sin(angle))
        #     if 0 <= x < self.resolution.width and 0 <= y < self.resolution.height:
        #         self.set_pixel(x, y, color)

        cv2.ellipse(self.frame_buffer, (cy, cx), (ry, rx), 0, 0, 360, color, thickness=thickness)

        with self._dirty_lock:
            self._dirty = True

    # --------------------------------------------------------------------------------
    def _bezier_quadratic(self, t, p0x: int, p0y: int, p1x: int, p1y: int, p2x: int, p2y: int):
        x = (1 - t) ** 2 * p0x + 2 * (1 - t) * t * p1x + t ** 2 * p2x
        y = (1 - t) ** 2 * p0y + 2 * (1 - t) * t * p1y + t ** 2 * p2y
        return int(x), int(y)

    # --------------------------------------------------------------------------------
    def draw_quadratic_bezier(self, p0x: int, p0y: int, p1x: int, p1y: int, p2x: int, p2y: int,
                              color: tuple[int, int, int]):
        """Draw a quadratic Bézier curve (P0, P1, P2) with smooth interpolation"""
        t = 0.0
        prev_x, prev_y = self._bezier_quadratic(t, p0x, p0y, p1x, p1y, p2x, p2y)
        while t < 1.0:
            # Adaptive step size based on local curve flatness
            dt = 0.001  # minimum step
            next_t = min(t + dt, 1.0)
            next_x, next_y = self._bezier_quadratic(next_t, p0x, p0y, p1x, p1y, p2x, p2y)

            # Increase step if next point is close
            while next_t < 1.0 and (next_x == prev_x and next_y == prev_y):
                next_t = min(next_t + dt, 1.0)
                next_x, next_y = self._bezier_quadratic(next_t, p0x, p0y, p1x, p1y, p2x, p2y)

            self.draw_line(prev_x, prev_y, next_x, next_y, color)
            prev_x, prev_y = next_x, next_y
            t = next_t

        with self._dirty_lock:
            self._dirty = True

    # --------------------------------------------------------------------------------
    def _bezier_cubic(self, t, p0x: int, p0y: int, p1x: int, p1y: int, p2x: int, p2y: int, p3x: int, p3y: int):
        x = (1 - t) ** 3 * p0x + 3 * (1 - t) ** 2 * t * p1x + 3 * (1 - t) * t ** 2 * p2x + t ** 3 * p3x
        y = (1 - t) ** 3 * p0y + 3 * (1 - t) ** 2 * t * p1y + 3 * (1 - t) * t ** 2 * p2y + t ** 3 * p3y
        return int(x), int(y)

    # --------------------------------------------------------------------------------
    def draw_cubic_bezier(self, p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, color):
        """Draw a cubic Bézier curve (P0, P1, P2, P3) with smooth interpolation"""
        t = 0.0
        prev_x, prev_y = self._bezier_cubic(t, p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y)
        while t < 1.0:
            dt = 0.001  # base step
            next_t = min(t + dt, 1.0)
            next_x, next_y = self._bezier_cubic(next_t, p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y)

            while next_t < 1.0 and (next_x == prev_x and next_y == prev_y):
                next_t = min(next_t + dt, 1.0)
                next_x, next_y = self._bezier_cubic(next_t, p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y)

            self.draw_line(prev_x, prev_y, next_x, next_y, color)
            prev_x, prev_y = next_x, next_y
            t = next_t

        with self._dirty_lock:
            self._dirty = True

    # --------------------------------------------------------------------------------
    def draw_text(self, text: str, x: int, y: int,
                  color: tuple[int, int, int],
                  antialias: bool = True,
                  line_spacing: int = 2,
                  font: Optional[pg.font.Font] = None,
                  bg_color: Optional[tuple[int, int, int]] = None):
        """Draw multiline text at (x, y) using Pygame's font rendering.
           Clips everything outside the virtual screen boundaries.
        """

        start = pg.time.get_ticks()

        lines = text.expandtabs(4).split('\n')
        current_y = y

        for line in lines:
            if not line.strip():
                current_y += font.get_linesize() + line_spacing
                continue

            text_surface = self.get_cached_text((line, antialias, color, bg_color, font))
            text_width, text_height = text_surface.get_size()

            # Clip the rendered surface to fit within screen bounds
            if current_y + text_height < 0 or current_y >= self.resolution.height:
                current_y += text_height + line_spacing
                continue  # Skip out-of-bounds lines

            for dy in range(text_height):
                screen_y = current_y + dy
                if 0 <= screen_y < self.resolution.height:
                    for dx in range(text_width):
                        screen_x = x + dx
                        if 0 <= screen_x < self.resolution.width:
                            r, g, b, a = text_surface.get_at((dx, dy))
                            if a > 0:
                                self.set_pixel(screen_x, screen_y, (r, g, b))

            current_y += text_height + line_spacing

        with self._dirty_lock:
            self._dirty = True

        elapsed = pg.time.get_ticks() - start
        print(f"Frame took {elapsed} ms")

    def get_cached_text(self,
                        key: tuple[str, bool, tuple[int, int, int], tuple[int, int, int], pg.font.Font]) -> Surface:
        try:
            return self.cached_texts[key]
        except KeyError:
            text, aliasing, color, bg_color, font = key
            surface = font.render(text, aliasing, color, bg_color)
            self.cached_texts[key] = surface
            return surface
        # TODO: Maybe fix a size limit for the text surface cache ?

    # --------------------------------------------------------------------------------
    def clear(self):
        """Clear the screen."""
        self.fill((0, 0, 0))
