import pygame
from pygame import Vector2, Surface

from .game_object import GameObject

class Sprite(GameObject):
    def __init__(self, image, pos):
        super().__init__()

        self.image = image
        self.mask: Optional[pygame.Mask] = None
        self.offset = Vector2(0, 0)
        self.position = Vector2(pos)

        self.rotation = 0
        self.flip_x = False
        self.flip_y = False
        self.visible = True

    def _blit(self, screen, show_masks=False):
        if self.visible:
            self.base_blit(self.image, self.get_global_position(), self.offset, self.rotation, self.flip_x, self.flip_y,
                           screen)

        if self.mask and show_masks:
            screen.blit(self.mask.to_surface(unsetcolor=[0]*4, setcolor=[255]*4),
                        self.get_global_position() - Vector2(self.mask.get_size()) // 2)

    @staticmethod
    def base_blit(image: Surface, global_position: Vector2, offset: Vector2,
                  rotation: int, flip_x: bool, flip_y: bool, screen: Surface):
        if not image:
            return
        rotated = pygame.transform.flip(image, flip_x, flip_y)
        rotated = pygame.transform.rotate(rotated, rotation)
        screen.blit(rotated,
                    global_position - Vector2(rotated.get_size()) // 2 + offset
                    )

    def is_intersecting_with(self, other) -> bool:
        return self.base_intersection(self.get_global_position(), self.mask, other.get_global_position(), other.mask)

    @staticmethod
    def base_intersection(position1, mask1, position2, mask2):
        if mask1 and mask2:
            mask_size_halved1 = Vector2(mask1.get_size()) / 2
            mask_size_halved2 = Vector2(mask2.get_size()) / 2
            offset = position1 - position2 - mask_size_halved2 + mask_size_halved1
            return bool(mask1.overlap(mask2, offset))
        return False
