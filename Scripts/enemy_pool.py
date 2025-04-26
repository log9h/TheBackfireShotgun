import pygame
from pygame import Vector2, Surface
from random import randint

from .constants import *
from .game_object import GameObject
from .player import Player
from .destroy_anim import DestroyAnim
from .shotgun_projectile import ShotgunProjectile
from .animator import *
from .sprite import Sprite


class EnemyPool(GameObject):
    def __init__(self, enemy_image: Surface, warning_image: Surface, player: Player):
        super().__init__()

        enemy_animator = Animator(ENEMY_MOVEMENT_SPEED)
        enemy_animator.add_animation('default', walk_animation, True)
        enemy_animator.set_current_animation('default')
        self.add_child(enemy_animator)

        self.player = player

        self.enemy_image = enemy_image
        self.warning_image = warning_image

        self.mask = pygame.Mask(ENEMY_MASK_SIZE)
        self.mask.fill()

        self.wave_timer = WAVE_SPAWN_TIMER
        self.wave_count = 0
        self.enemy_count = 0

        self.enemy_warnings = []
        self.warning_rotation = 0

        self.enemies = []  # [position, hp]
        self.enemy_collisions = {}
        self.warning_timer = ENEMY_WARNING_TIMER
        self.offset = Vector2(0, 0)
        self.rotation = 0
        self.enemy_speed = ENEMY_MOVEMENT_SPEED

    def _update(self, *args, **kwargs):
        if self.player.dead:
            return

        self.wave_timer -= 1
        if self.wave_timer == 0:
            self.enemy_count = 5 + self.wave_count
            self.wave_count += 1
            for _ in range(self.enemy_count):
                self.add_enemy_warning()

            self.wave_timer = WAVE_SPAWN_TIMER

        if self.enemy_warnings:
            self.warning_timer -= 1
        if self.warning_timer == 0:
            self.warning_timer = ENEMY_WARNING_TIMER

            while self.enemy_warnings:
                self.spawn_enemy(self.enemy_warnings.pop())
        else:
            self.warning_rotation += 1

        for i, _ in enumerate(self.enemies):
            self.enemies[i][0].move_towards_ip(self.player.get_global_position(), self.enemy_speed)

        checked = set()
        for i, (position1, hp1) in enumerate(self.enemies):
            for j, (position2, hp2) in enumerate(self.enemies):
                if i == j:
                    continue

                key = tuple(sorted((i, j)))
                if key in checked:
                    continue
                checked.add(key)

                diff = (position1 - position2)

                quarter_mask_sizes_sum = Vector2(self.mask.get_size()) / 4 * hp1 ** 0.5 + \
                    Vector2(self.mask.get_size()) / 4 * hp2 ** 0.5

                if abs(diff.x) <= quarter_mask_sizes_sum.x and abs(diff.y) <= quarter_mask_sizes_sum.y:
                    health_sum = hp1 + hp2
                    health_position_mod = min(hp1 / health_sum, hp2 / health_sum) if hp1 > hp2 else \
                        max(hp1 / health_sum, hp2 / health_sum)

                    self.enemies[i][0] = position1 + diff * health_position_mod
                    self.enemies[i][1] = hp1 + hp2
                    del self.enemies[j]
                break

    def _blit(self, screen, show_masks=False):
        for position in self.enemy_warnings:
            Sprite.base_blit(self.warning_image, position, Vector2(0, 0), self.warning_rotation, False, False, screen)
        for position, hp in self.enemies:
            sized = pygame.transform.scale_by(self.enemy_image, hp ** 0.5)
            Sprite.base_blit(sized, position, self.offset, self.rotation, False, False, screen)

            if show_masks:
                scaled_mask_size = list(map(lambda x: x * hp ** 0.5, self.mask.get_size()))

                scaled_mask = self.mask.scale(scaled_mask_size).to_surface(
                    unsetcolor=[0] * 4, setcolor=[255] * 4)
                screen.blit(scaled_mask, position - Vector2(scaled_mask.get_size()) // 2)

    def add_enemy_warning(self):
        mask_size_halved = Vector2(self.mask.get_size()) // 2
        self.enemy_warnings.append(Vector2(
            randint(int(mask_size_halved.x), GAME_SURFACE_SIZE[0] - mask_size_halved.x),
            randint(int(mask_size_halved.y), GAME_SURFACE_SIZE[1] - mask_size_halved.y))
        )

    def spawn_enemy(self, position: Vector2, hp=1):
        self.enemies.append([position, hp])
        self.enemy_collisions[len(self.enemies) - 1] = []

    def handle_collisions(self, other: GameObject):
        if type(other) is ShotgunProjectile and not other.deadly:
            return
        for i, (position, hp) in enumerate(self.enemies):
            scaled_mask_size = list(map(lambda x: x * hp ** 0.5, self.mask.get_size()))

            if Sprite.base_intersection(other.get_global_position(), other.mask,
                                        position, self.mask.scale(scaled_mask_size)):
                if other not in self.enemy_collisions[i]:
                    if type(other) is Player and not other.dead:
                        other.spawn_die_anim()
                    else:
                        self.enemy_collisions[i].append(other)
                        self.damage_enemy(i)
            elif other in self.enemy_collisions[i]:
                self.enemy_collisions[i].remove(other)

    def damage_enemy(self, index: int):
        self.enemies[index][1] -= 1

        destroy_anim = DestroyAnim(self.enemy_image, self.enemies[index][0], 0,
                                   False, False)
        destroy_anim.x_speed = randint(-5, 6)
        self.get_root().add_child(destroy_anim)
        if self.enemies[index][1] == 0:
            del self.enemies[index]
