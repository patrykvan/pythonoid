import random

import pygame
from pygame.rect import Rect

from bonus import Bonus
from settings import BLOCK_COLORS


class Block(pygame.Surface):
    """
    Hittable block
    Returns: Block object
    Functions: update
    """

    def __init__(self, top, left, width, height, life):
        super().__init__((width, height))
        self.rect = Rect(top, left, width, height)
        self.life = life
        self.bonus = Bonus(self.rect)
        self.update()

    def get_rect(self):
        return self.rect

    def update(self):
        self.fill(pygame.Color(self._get_color()))

    def _get_color(self):
        return BLOCK_COLORS[self.life - 1] if len(BLOCK_COLORS) > self.life > 0 else BLOCK_COLORS[-1]
