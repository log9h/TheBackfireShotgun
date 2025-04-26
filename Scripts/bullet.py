import pygame

from .utils import *
from .sprite import Sprite
from .constants import BULLET_MASK_SIZE, BULLET_SPEED

class Bullet(Sprite):
    def __init__(self, pos, rotation):
        image_surface = pygame.Surface(BULLET_MASK_SIZE)
        image_surface.fill([255]*4)
        image_surface.set_colorkey([0]*4)

        super().__init__(image_surface, pos)

        self.rotation = rotation
        rotated = pygame.transform.rotate(image_surface, self.rotation)

        self.mask = pygame.mask.from_surface(rotated)

        self.lifetime = 300

    def _update(self, *args, **kwargs):
        self.position += BULLET_SPEED * angle_to_vector(self.rotation)

        self.lifetime -= 1
        if self.lifetime < 0:
            self.parent.children.remove(self)
