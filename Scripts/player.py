import pygame
from pygame import Surface, Vector2
from typing import Dict, Tuple

from .utils import *
from .constants import *
from .animator import *
from .sprite import Sprite
from .destroy_anim import DestroyAnim
from .shotgun import Shotgun
from .shotgun_projectile import ShotgunProjectile

class Player(Sprite):
    def __init__(self, image: Surface, pos: Vector2):
        super().__init__(image, pos)

        self.dead = False

        self.mask = pygame.Mask(PLAYER_MASK_SIZE)
        self.mask.fill()

        self.animator = Animator(2)
        self.animator.add_animation('walk', walk_animation, True)
        self.animator.add_animation('idle', idle_animation, False)
        self.add_child(self.animator)

        self.movement_speed = PLAYER_MOVEMENT_SPEED

    def _update(self, keys: Dict[int, bool], mouse_pos: Tuple[int, int]):
        movement = pygame.Vector2()
        movement.x = (keys[pygame.K_d] - keys[pygame.K_a]) * self.movement_speed
        movement.y = (keys[pygame.K_s] - keys[pygame.K_w]) * self.movement_speed
        wall_collisions = screen_border_check(self.position + movement, self.mask.get_size())

        if not (wall_collisions[0] or wall_collisions[1]):
            self.position.x += movement.x
        if not (wall_collisions[2] or wall_collisions[3]):
            self.position.y += movement.y

        if any(movement):
            self.animator.set_current_animation('walk')

            if not (movement.x > 0) ^ self.flip_x:
                self.flip_x = not self.flip_x
        else:
            self.animator.set_current_animation('idle')

    def shotgun_projectile_collision(self, projectile: ShotgunProjectile):
        if projectile.player_immunity > 0 or self.dead:
            return

        if projectile.deadly:
            self.spawn_die_anim()
        else:
            self.reload_shotgun()

    def spawn_die_anim(self):
        self.dead = True
        self.get_root().add_child(DestroyAnim(self.image, self.get_global_position(), 0,
                                              self.flip_x, True))
        self.get_root().screen_shake = 15
        self.destroy()

    def reload_shotgun(self):
        shotgun = self.get_child_by_class(Shotgun)
        shotgun.reload()
