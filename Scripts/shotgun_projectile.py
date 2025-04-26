import pygame
from pygame import Vector2, Surface

from .constants import *
from .utils import *
from .sprite import Sprite

class ShotgunProjectile(Sprite):
    def __init__(self, image: Surface, pos: Vector2, rotation: int, flip_x: bool, flip_y: bool):
        super().__init__(image, pos)

        self.prev_pos = pygame.Vector2(0, 0)
        self.trace = None

        self.update_mask()

        self.speed = SHOTGUN_INITIAL_SPEED
        self.rotation_speed = SHOTGUN_RPS
        self.full_speed_time = SHOTGUN_FULL_SPEED_TIME

        self.movement_vector = angle_to_vector(rotation)

        self.rotation = rotation
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.clockwise = self.flip_y

        self.player_immunity = 30
        self.deadly = True

        self.wall_reflect_cooldowns = [0, 0]
        self.previous_wall_reflection = [False, False]

    def _update(self, *args, **kwargs):
        self.player_immunity = max(0, self.player_immunity - 1)
        self.prev_pos = self.position.copy()

        rotation = 360 * self.rotation_speed / 60
        self.rotation -= rotation if self.clockwise else -rotation

        self.full_speed_time = max(0, self.full_speed_time - 1)
        if self.full_speed_time == 0:
            self.speed = max(0, self.speed - SHOTGUN_DECELERATION_MOD / 60)
            self.rotation_speed = max(0, self.rotation_speed - SHOTGUN_DECELERATION_MOD / 120)

        self.deadly = self.speed >= SHOTGUN_DEADLY_SPEED_THRESHOLD

        self.position += self.speed * self.movement_vector

        self.wall_reflect_cooldowns[0] = max(0, self.wall_reflect_cooldowns[0] - 1)
        self.wall_reflect_cooldowns[1] = max(0, self.wall_reflect_cooldowns[1] - 1)

        if not any(self.wall_reflect_cooldowns):
            self.wall_reflect_check()

        self.update_mask()

    def update_mask(self):
        rotated = pygame.transform.flip(self.image, self.flip_x, self.flip_y)
        rotated = pygame.transform.rotate(rotated, self.rotation)
        self.mask = pygame.mask.from_surface(rotated)

    def _blit(self, screen, show_masks=False):
        mask_surface = self.mask.to_surface(setcolor=SHOTGUN_TRACE_COLOR, unsetcolor=[0] * 4)
        alpha = (self.speed - SHOTGUN_DEADLY_SPEED_THRESHOLD) / 2* 255
        mask_surface.set_alpha(alpha)
        if not self.deadly:
            mask_surface.set_alpha(128)
            mask_surface = pygame.transform.invert(mask_surface)
        pos_diff = self.position - self.prev_pos
        screen.blit(mask_surface,
                    self.get_global_position() - 2 * pos_diff - pygame.Vector2(mask_surface.get_size()) // 2
                    )
        super()._blit(screen, show_masks)

    def wall_reflect_check(self):
        wall_collisions = screen_border_check(self.position, self.mask.get_size())

        reflected = False
        if wall_collisions[0] and self.movement_vector.x < 0 or \
                wall_collisions[1] and self.movement_vector.x > 0:
            self.movement_vector.x *= -1
            reflected = True
        if wall_collisions[2] and self.movement_vector.y < 0 or \
                wall_collisions[3] and self.movement_vector.y > 0:
            self.movement_vector.y *= -1
            reflected = True

        if reflected:
            self.clockwise = not self.clockwise
