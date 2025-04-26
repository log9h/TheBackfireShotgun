import pygame
from pygame import Vector2
import math

from .sprite import Sprite
from .bullet import Bullet
from .destroy_anim import DestroyAnim
from .shotgun_projectile import ShotgunProjectile

class Shotgun(Sprite):
    def __init__(self, images, pos, base_offset, shot_point_offset):
        self.images = images
        super().__init__(images[1], pos)

        self.base_offset = base_offset
        self.offset = self.base_offset[:]

        self.shot_point_offset = pygame.Vector2(shot_point_offset)
        self.shot_point = pygame.Vector2()
        self.update_shot_point()

        self.projectile = None
        self.used = False

        self.cooldown = 0

    def _update(self, keys, mouse_pos):
        rel_pos = mouse_pos - self.get_global_position()

        self.rotation = (180 / math.pi) * -math.atan2(rel_pos.y, rel_pos.x)
        self.offset = self.base_offset[:]
        if self.rotation > 90 or self.rotation < -90:
            self.flip_y = True
            self.offset[0] *= -1
        else:
            self.flip_y = False
        
        if self.used:
            self.visible = False
            self.image = self.images[2]
            self.offset[0] = 0
            self.rotation = self.rotation - 180 if self.rotation > 0 else self.rotation + 180
        else:
            self.visible = True
            self.image = self.images[1]

        self.reflect_parent()
        self.update_shot_point()

        self.cooldown = max(0, self.cooldown - 1)
        if pygame.mouse.get_just_pressed()[0] and self.cooldown == 0:
            if not self.used:
                self.shoot()
            else:
                self.try_grab()
            self.cooldown = 30

    def reflect_parent(self):
        self.offset += self.parent.offset
        self.rotation += self.parent.rotation * 0.5

    def update_shot_point(self):
        rotated_offset = self.shot_point_offset.rotate(-self.rotation) + self.offset
        global_position = self.get_global_position()
        self.shot_point.xy = global_position.x + rotated_offset[0], global_position.y + 0.75 * rotated_offset[1]

    def shoot(self):
        self.used = True
        self.get_root().screen_shake = 15

        root = self.get_root()
        for i in range(9):
            root.add_child(Bullet(self.shot_point, self.rotation - 30 + i * 6.67))

        backward_angle = self.rotation - 180 if self.rotation > 0 else self.rotation + 180
        shotgun_projectile = ShotgunProjectile(self.images[0], self.get_global_position(), backward_angle,
                                               not self.flip_x, not self.flip_y)
        self.projectile = shotgun_projectile
        root.add_child(shotgun_projectile)

    def reload(self):
        self.used = False
        self.cooldown = 0

        anim = DestroyAnim(self.images[3], self.get_global_position(), self.rotation,
                           not self.flip_x, False)
        anim.x_speed = 2 if self.flip_y else -2
        anim.rotation_speed = -20
        anim.speed = 0.5
        anim.y_speed = 1.5
        self.get_root().add_child(anim)

        self.projectile.destroy()

    def try_grab(self):
        pass
