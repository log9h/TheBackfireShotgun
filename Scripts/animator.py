from pygame import Vector2

from dataclasses import dataclass
from collections import namedtuple
from typing import List, Dict, Union, Any

from .utils import *
from .game_object import GameObject

@dataclass
class AttributeValue:
    name: str
    attr_type: type
    value: Any

@dataclass
class Keyframe:
    attribute_values: Dict[str, Any]
    time: float

@dataclass
class Animation:
    keyframes: List[Keyframe]
    loop: bool

AnimationMetadata = namedtuple('AnimationMetadata', ['attributes', 'length'])

walk_animation = [
    Keyframe({'offset': Vector2(-3, -6),
              'rotation': -15}, 15),

    Keyframe({'offset': Vector2(0, -2),
              'rotation': 0}, 30),

    Keyframe({'offset': Vector2(3, -6),
              'rotation': 15}, 45),

    Keyframe({'offset': Vector2(0, 0),
              'rotation': 0}, 60)
]

idle_animation = [
    Keyframe({'offset': None,
              'rotation': None}, 0),
    Keyframe({'offset': Vector2(0, 0),
              'rotation': 0}, 60)
]

class Animator(GameObject):
    def __init__(self, animation_speed=1):
        super().__init__()

        self.animations = {}
        self.animations_metadata = {}

        self.current_animation = ''
        self.current_animation_progress = 0

        self.animation_speed = animation_speed

    def add_animation(self, name: str, keyframes: List[Keyframe], loop: bool):
        animation_attributes = set()
        for keyframe in keyframes:
            for attr in keyframe.attribute_values.keys():
                animation_attributes.add(attr)

        self.animations[name] = Animation(keyframes, loop)
        self.animations_metadata[name] = AnimationMetadata(animation_attributes, max(k.time for k in keyframes))

    def set_current_animation(self, name: str):
        if self.current_animation != name and name in self.animations.keys():
            self.current_animation = name
            self.current_animation_progress = 0

    def _update(self, *args, **kwargs):
        if self.current_animation is None:
            return

        animation: Animation = self.animations[self.current_animation]
        metadata: AnimationMetadata = self.animations_metadata[self.current_animation]
        keyframes: List[Keyframe] = animation.keyframes

        self.current_animation_progress += self.animation_speed
        if self.current_animation_progress >= metadata.length:
            if not animation.loop:
                return
            self.current_animation_progress %= metadata.length

        current_keyframe_index = sum(self.current_animation_progress >= keyframe.time for keyframe in keyframes) - 1
        next_keyframe_index = current_keyframe_index + 1

        current_progress = self.current_animation_progress
        previous_keyframe_time = 0
        for keyframe in keyframes:
            current_keyframe_length = keyframe.time - previous_keyframe_time

            if current_keyframe_length <= current_progress:
                current_progress -= current_keyframe_length
            else:
                current_progress /= current_keyframe_length
                break
            previous_keyframe_time = keyframe.time

        for attr in metadata.attributes:
            start_value = animation.keyframes[current_keyframe_index].attribute_values[attr]
            if start_value is None:
                start_value = getattr(self.parent, attr)

            end_value = animation.keyframes[next_keyframe_index].attribute_values[attr]

            setattr(self.parent, attr, lerp(start_value, end_value, current_progress))
