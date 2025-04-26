import pygame

from .sprite import Sprite
from .constants import *

class DestroyAnim(Sprite):
    def __init__(self, image: pygame.surface.Surface, pos, rotation, flip_x, trace=False):
        super().__init__(image, pos)
        self.rotation = rotation
        self.flip_x = flip_x

        if trace:
            self.trace_opacity = 255
            self.trace_pos = pos
        else:
            self.trace_pos = None

        self.speed = 1

        self.rotation_speed = 2
        self.x_speed = 0
        self.y_speed = 1
        self.lifetime = 150

    def _update(self, *args, **kwargs):
        t = (150 - self.lifetime) / 300
        self.y_speed -= 9.81 * t

        self.position.x += self.x_speed * self.speed
        self.position.y -= 2 * self.y_speed / self.speed

        self.rotation += self.rotation_speed if not self.flip_x else -self.rotation_speed
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.parent.children.remove(self)

    def _blit(self, screen, show_masks=False):
        if self.trace_pos is not None:
            trace_opacity = self.lifetime / 150 * 255
            trace = pygame.mask.from_surface(self.image).to_surface(setcolor=[255, 0, 77, trace_opacity],
                                                                    unsetcolor=[0]*4)
            screen.blit(trace,
                        self.trace_pos - pygame.Vector2(trace.get_size()) // 2
                        )
        super()._blit(screen, show_masks)
