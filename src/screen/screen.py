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



