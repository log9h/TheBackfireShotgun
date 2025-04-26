from __future__ import annotations
from typing import final

import pygame
from pygame import Vector2, Surface

class GameObject:
    def __init__(self):
        super().__init__()

        self.position = Vector2(0, 0)

        self.parent = None
        self.children = []

    def _update(self, *args, **kwargs):
        pass

    @final
    def update(self, *args, **kwargs):
        self._update(*args, **kwargs)
        for child in self.children:
            child.update(*args, **kwargs)

    def _blit(self, screen: Surface, show_masks=False):
        pass

    @final
    def blit(self, screen: Surface, show_masks=False):
        self._blit(screen, show_masks)
        for child in self.children:
            child.blit(screen, show_masks)

    def get_global_position(self):
        global_position = self.position.copy()
        if self.parent:
            global_position += self.parent.get_global_position()
        return global_position

    def get_child_by_class(self, cls: type) -> object:
        for child in self.children:
            if isinstance(child, cls):
                return child

    def add_child(self, child: GameObject):
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def remove_child(self, child: GameObject):
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def get_root(self) -> GameObject:
        current_parent = self
        while current_parent.parent:
            current_parent = current_parent.parent
        return current_parent

    def destroy(self):
        self.parent.remove_child(self)
