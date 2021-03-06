import math
import random

import pygame

import soundmixer as soundmixer
from load_utils import load_png
from settings import BALL_IMG, BALL_LOSS, PADDLE_HIT, MAX_FPS, BASE_SPEED
from surface_utils import SurfaceUtils


class Ball(pygame.sprite.Sprite):
    """
    Moving ball
    Returns: Ball object
    Functions: reinit, update
    """

    MAX_RESIZE_TIMES = 1
    MAX_SPEED_CHANGE = 2
    SUPER_BALL_TIME = 160
    DEFAULT_BALL = None
    SUPER_BALL_IMG = None

    def __init__(self, area, vector=None):
        super().__init__()
        self.resize_state = self.speed_state = self.super_ball_time = 0
        self.image = self.rect = None
        self.area = area
        self.active = True
        if vector:
            self.vector = vector
        else:
            self.vector = random.uniform(1.25, math.pi - 1.25), BASE_SPEED / MAX_FPS
        self.custom_angle = self.col_paddle = self.col_wall = self.hit = self.tl = self.tr = self.bl = self.br = False
        self.reinit()

    def reinit(self):
        if not Ball.DEFAULT_BALL:
            Ball.DEFAULT_BALL = load_png(BALL_IMG)
        self.image, self.rect = Ball.DEFAULT_BALL
        if not Ball.SUPER_BALL_IMG:
            Ball.SUPER_BALL_IMG = SurfaceUtils.color_surface(self.image, pygame.Color('Purple'))
        self.rect.center = self.area.center
        self.resize_state = self.speed_state = 0

    def update(self):
        if self.super_ball_time:
            self.super_ball_time -= 1
            if not self.super_ball_time:
                self.image, _ = Ball.DEFAULT_BALL
        newpos = self.calcnewpos(self.rect, self.vector)
        self.rect = newpos
        (angle, z) = self.vector

        if self.custom_angle:
            self.vector = (self.custom_angle, z)
            self.custom_angle = None
            return

        if not self.area.contains(newpos):
            if not self.col_wall:
                self.col_wall = True
                tl = not self.area.collidepoint(newpos.topleft)
                tr = not self.area.collidepoint(newpos.topright)
                bl = not self.area.collidepoint(newpos.bottomleft)
                br = not self.area.collidepoint(newpos.bottomright)

                if br and bl:
                    self.active = False
                    soundmixer.solochanneleffect(BALL_LOSS)
                    return
                angle *= -1
                if tr and br:
                    angle -= math.pi
                elif tl and bl:
                    angle += math.pi
                soundmixer.solochanneleffect(PADDLE_HIT)
        else:
            self.col_wall = False
            if self.hit and not self.col_paddle:
                angle *= -1
                soundmixer.solochanneleffect(PADDLE_HIT)
                if self.tr and self.br:
                    angle -= math.pi
                elif self.tl and self.bl:
                    angle += math.pi
                self.col_paddle = True
            elif not self.hit and self.col_paddle:
                self.col_paddle = False
        self.vector = (angle, z)

    def calcnewpos(self, rect, vector):
        (angle, z) = vector
        (dx, dy) = (round(z * math.cos(angle), 0), round(z * math.sin(angle), 0))
        return rect.move(dx, dy)

    def shrink(self):
        if self.resize_state != -self.MAX_RESIZE_TIMES:
            self._resize_by(0.8)
            self.resize_state -= 1

    def expand(self):
        if self.resize_state != self.MAX_RESIZE_TIMES:
            self._resize_by(1.2)
            self.resize_state += 1

    def _resize_by(self, by):
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width() * by),
                                                         (round(self.image.get_height() * by))))
        old_pos = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = old_pos
        if not self.area.contains(self.rect):
            self.rect.center = self.area.center

    def slow_down(self):
        if self.speed_state != -self.MAX_SPEED_CHANGE:
            v, speed = self.vector
            speed *= 0.7
            self.vector = v, speed
            self.speed_state -= 1

    def speed_up(self):
        if self.speed_state != self.MAX_SPEED_CHANGE:
            v, speed = self.vector
            speed *= 1.3
            self.vector = v, speed
            self.speed_state += 1

    def is_super_ball(self):
        return self.super_ball_time

    def super_ball(self):
        self.super_ball_time = Ball.SUPER_BALL_TIME
        self.image = Ball.SUPER_BALL_IMG
