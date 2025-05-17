################################################################################
import math
from fractions import Fraction
from threading import Lock
from typing import Optional

from pygame.time import Clock

import pygame as pg
import numpy as np
import cupy as cp
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
        self.frame_buffer = cp.zeros((width, height, 3), dtype=np.uint8)
        self.is_on = False
        self.refresh_rate = hz
        pg.init()
        self.screen: Optional[Surface] = None
        self.surface = pg.Surface((self.resolution.width, self.resolution.height))
        self.clock: Clock = pg.time.Clock()
        self.brightness: float = brightness
        self.bright_frame = None
        self._dirty = False
        self.cached_texts: dict[tuple[str, bool, tuple, tuple, pg.font.Font], pg.Surface] = {}
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
                    self.bright_frame = cp.clip(self.frame_buffer.astype(np.float16) * self.brightness, 0, 255).astype(np.uint8)
                else:
                    self.bright_frame = self.frame_buffer.copy()
                pg.surfarray.blit_array(self.surface, cp.asnumpy(self.bright_frame))
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
    def set_pixel(self, x: int, y: int, color: cp.ndarray):
        self.frame_buffer[x, y] = color

    # --------------------------------------------------------------------------------
    def fill(self, color: cp.ndarray):
        self.frame_buffer[:, :] = color

    # --------------------------------------------------------------------------------
    def set_refresh_rate(self, hz: int):
        self.refresh_rate = hz

    # --------------------------------------------------------------------------------
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: cp.ndarray):
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
    def draw_rectangle(self, x: int, y: int, width: int, height: int, color: cp.ndarray, fill: bool = False):
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

    # --------------------------------------------------------------------------------
    def draw_arc(self, cx: int, cy: int, radius: int, angle_start: int, angle_end: int,
                 color: cp.ndarray):
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
    def draw_circle(self, cx: int, cy: int, radius: int, color: cp.ndarray, thickness: int = 1):

        self.draw_ellipse(cx, cy, radius, radius, color, thickness)

    # --------------------------------------------------------------------------------
    def draw_ellipse(self, cx: int, cy: int, rx: int, ry: int, color: cp.ndarray, thickness: int = 1):
        """Draw an ellipse using polar coordinates"""

        h, w = self.frame_buffer.shape[:2]
        if thickness < 0:
            self._draw_elipse_filled(cx, cy, rx, ry, color, h, w)
        else:
            self._draw_ellipse_outlined(cx, cy, rx, ry, color, thickness, h, w)

    # --------------------------------------------------------------------------------
    def _draw_elipse_filled(self, cx: int, cy: int, rx: int, ry: int, color: cp.ndarray, _h, _w):

        # Create coordinate grids
        x, y = cp.indices((_h, _w))

        # Ellipse equation (shifted to center)
        ellipse = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2

        # Create mask (automatically handles out-of-bounds)
        mask = ellipse <= 1.0

        # Apply color to all channels
        self.frame_buffer[mask] = color

        with self._dirty_lock:
            self._dirty = True

    # --------------------------------------------------------------------------------
    def _draw_ellipse_outlined(self, cx: int, cy: int, rx: int, ry: int, color: cp.ndarray, thickness: int, _h, _w):

        # Create coordinate grids
        x, y = cp.indices((_h, _w))

        # Calculate normalized distance from ellipse boundary
        # This gives us exact pixel distances from the edge
        distance = cp.sqrt((x - cx) ** 2 * ry ** 2 + (y - cy) ** 2 * rx ** 2) - (rx * ry)

        # Convert distance to pixels
        distance_px = distance / cp.clip(cp.sqrt(rx ** 2 * ((y - cy) / ry) ** 2 + ry ** 2 * ((x - cx) / rx) ** 2),
                                         1e-6, None)

        # Create mask for outline
        if thickness <= 1:
            # For thin outlines, use exact boundary
            mask = cp.abs(distance_px) <= 0.5
        else:
            # For thicker outlines, create band
            outer = distance_px <= (thickness / 2)
            inner = distance_px <= -(thickness / 2)
            mask = outer & ~inner

        # Handle completely filled small ellipses
        if thickness >= min(rx, ry):
            mask = distance <= 0

        self.frame_buffer[mask] = color

        with self._dirty_lock:
            self._dirty = True

    # --------------------------------------------------------------------------------
    @staticmethod
    def _bezier_quadratic(t, p0x: int, p0y: int, p1x: int, p1y: int, p2x: int, p2y: int):
        x = (1 - t) ** 2 * p0x + 2 * (1 - t) * t * p1x + t ** 2 * p2x
        y = (1 - t) ** 2 * p0y + 2 * (1 - t) * t * p1y + t ** 2 * p2y
        return int(x), int(y)

    # --------------------------------------------------------------------------------
    def draw_quadratic_bezier(self, p0x: int, p0y: int, p1x: int, p1y: int, p2x: int, p2y: int,
                              color: cp.ndarray):
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
    @staticmethod
    def _bezier_cubic(t, p0x: int, p0y: int, p1x: int, p1y: int, p2x: int, p2y: int, p3x: int, p3y: int):
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
                  color: cp.ndarray,
                  antialias: bool = True,
                  line_spacing: int = 2,
                  font: Optional[pg.font.Font] = None,
                  bg_color: Optional[cp.ndarray] = None):
        """Efficiently draw multiline text at (x, y) using batch transfer to GPU (W, H, 3 layout)."""
        lines = text.expandtabs(4).split('\n')
        current_y = y

        for line in lines:
            if not line.strip():
                current_y += font.get_linesize() + line_spacing
                continue

            color_cpu = tuple(color.get().tolist())
            bg_color_cpu = tuple(bg_color.get().tolist()) if bg_color is not None else None

            # Get or render text surface
            surface = self.get_cached_text((line, antialias, color_cpu, bg_color_cpu, font))
            width, height = surface.get_size()

            if current_y + height < 0 or current_y >= self.resolution.height:
                current_y += height + line_spacing
                continue

            # Get raw image and alpha channel from Pygame surface (shape: (W, H, 3) and (W, H))
            surface = surface.convert_alpha()
            rgb_np = pg.surfarray.array3d(surface)  # shape: (W, H, 3)
            alpha_np = pg.surfarray.array_alpha(surface)  # shape: (W, H)

            # Convert to GPU arrays
            rgb_cp = cp.asarray(rgb_np, dtype=cp.uint8)
            alpha_cp = cp.asarray(alpha_np, dtype=cp.uint8)

            # Compute dimensions
            w, h = rgb_cp.shape[:2]
            max_x = min(self.resolution.width, x + w)
            max_y = min(self.resolution.height, current_y + h)
            draw_width = max_x - x
            draw_height = max_y - current_y
            if draw_width <= 0 or draw_height <= 0:
                current_y += height + line_spacing
                continue

            # Slice only visible area
            rgb_cp = rgb_cp[:draw_width, :draw_height]
            alpha_cp = alpha_cp[:draw_width, :draw_height]

            # Alpha mask
            mask = alpha_cp > 0

            # Apply masked text
            target_slice = self.frame_buffer[x:max_x, current_y:max_y]  # Shape: (W, H, 3)
            target_slice[mask] = rgb_cp[mask]

            current_y += height + line_spacing

        with self._dirty_lock:
            self._dirty = True

    # --------------------------------------------------------------------------------
    def get_cached_text(self,
                        key: tuple[str, bool, tuple, tuple, pg.font.Font]) -> Surface:
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
        self.fill(cp.array([0, 0, 0]))
