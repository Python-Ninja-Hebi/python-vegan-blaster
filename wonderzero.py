from __future__ import annotations
from typing import List
import pygame
from pygame import Color,Surface,Vector2

import asyncio

import inspect

# -- colors --
MAROON = (128, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
OLIVE = (128, 128, 0)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
FUCHSIA = (255, 0, 255)
LIME = (0, 255, 0)
TEAL = (0, 128, 128)
AQUA = (0, 255, 255)
BLUE = (0, 0, 255)
NAVY = (0, 0, 128)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARKGRAY = (169,169,169)
SILVER = (192, 192, 192)
WHITE = (255, 255, 255)

# -- interfaces --
class GameInterface:
    def update(self, delta_time:float):
        pass
    def draw(self, screen:Surface):
        pass

# -- gameloop --
class Game:

    def __init__(self,height:int=600, width:int=800, name:str="no name", update=None,draw=None):
        self.height:int = height
        self.width:int = width
        self.name:str = name
        self.update = update
        self.draw = draw
        self.background_color:Color = BLACK
        self.frames_per_second:int = 30

        if self.draw is None and "draw" in inspect.stack()[1][0].f_globals:
            self.draw = inspect.stack()[1][0].f_globals["draw"]

        if self.update is None and "update" in inspect.stack()[1][0].f_globals:
            self.update = inspect.stack()[1][0].f_globals["update"]
    def run(self):
        clock, running = self.init_loop()

        while running:
            running = self.do_loop(clock, running)

    async def run_async(self):
        clock, running = self.init_loop()

        while running:
            running = self.do_loop(clock, running)
            await asyncio.sleep(0)

    def init_loop(self):
        pygame.init()
        pygame.display.set_caption(self.name)
        self.screen: Surface = pygame.display.set_mode((self.width, self.height))
        running = True
        clock = pygame.time.Clock()
        return clock, running

    def do_loop(self, clock, running):
        # ---- input ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # ---- update ----
        delta_time = clock.tick(self.frames_per_second) / 1000.0  # time since last frame
        if self.update:
            self.update(delta_time)
        # ---- draw ----
        self.screen.fill(self.background_color)
        if self.draw:
            self.draw(self.screen)
        pygame.display.flip()
        return running

    def quit(self):
        pygame.quit()

TEXT_ALIGNMENT_LEFT = 1
TEXT_ALIGNMENT_MID = 2

def draw_text(screen: Surface, text:str, size: int, color, position: Vector2,
              alignment=TEXT_ALIGNMENT_LEFT) -> None:

    font = pygame.font.Font(None, size)
    position = Vector2(position.x, position.y)

    img = font.render(text, True, color)
    rect: Rect = img.get_rect()
    if alignment == TEXT_ALIGNMENT_LEFT:
        rect.topleft = position
    else:
        rect.midtop = position

    screen.blit(img, rect)