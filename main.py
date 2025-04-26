import pygame
from pygame import Vector2

from Scripts.constants import *
from Scripts.player import Player
from Scripts.shotgun import Shotgun
from Scripts.shotgun_projectile import ShotgunProjectile
from Scripts.game_object import GameObject
from Scripts.bullet import Bullet
from Scripts.enemy_pool import EnemyPool

from random import randint

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
clock = pygame.time.Clock()

window_size_mod = 1
def adjust_size_mod():
    global window_size_mod
    actual_window_size = pygame.display.get_surface().get_size()

    size_mod_x_relative = actual_window_size[0] / GAME_SURFACE_SIZE[0]
    size_mod_y_relative = actual_window_size[1] / GAME_SURFACE_SIZE[1]
    window_size_mod = min(size_mod_x_relative, size_mod_y_relative)

def load_and_scale_image(path):
    return pygame.transform.scale_by(pygame.image.load(path), SIZE_MOD)

font3_4 = pygame.font.Font('Assets/3x4 pixel font.ttf', 16)

root, plr, enemy_pool = None, None, None
def init():
    global root, plr, enemy_pool
    root = GameObject()
    root.screen_shake = 0

    plr = Player(load_and_scale_image('Assets/player.png'), Vector2(120, 90))
    root.add_child(plr)

    enemy_pool = EnemyPool(load_and_scale_image('Assets/slime.png'),
                           load_and_scale_image('Assets/enemy_warning.png'), plr)
    root.add_child(enemy_pool)

    shotgun_images = (
        load_and_scale_image('Assets/shotgun.png'),
        load_and_scale_image('Assets/shotgun_hold.png'),
        load_and_scale_image('Assets/grab_preview.png'),
        load_and_scale_image('Assets/shotgun_shell.png'),
    )
    shotgun = Shotgun(shotgun_images, (0, 0), [4, 0], [15, 0])
    plr.add_child(shotgun)
init()

show_masks = False
reset_timer = 0

game_surface = pygame.surface.Surface((240, 180))

running = True
while running:
    game_surface.fill(BACKGROUND_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                show_masks = not show_masks
            if event.key == pygame.K_r and reset_timer == 0:
                reset_timer = 60

    if reset_timer > 0:
        screen.fill([0] * 3)
        if reset_timer > 30:
            root.screen_shake = 1
            alpha = (reset_timer - 30) * 255 / 30
        elif reset_timer < 30:
            alpha = 255 - reset_timer * 255 / 30
        else:
            alpha = 0
            init()
            root.screen_shake = 15
        game_surface.set_alpha(int(alpha))
        reset_timer -= 1

    for child1 in root.children:
        child1_type = type(child1)
        if child1_type is ShotgunProjectile and plr.is_intersecting_with(child1):
            plr.shotgun_projectile_collision(child1)

        if child1_type is Bullet:
            if plr.is_intersecting_with(child1) and not plr.dead:
                plr.spawn_die_anim()
        enemy_pool.handle_collisions(child1)
    adjust_size_mod()

    relative_mouse_pos = Vector2(pygame.mouse.get_pos()) / window_size_mod
    root.update(keys=pygame.key.get_pressed(), mouse_pos=relative_mouse_pos)
    root.blit(game_surface, show_masks)

    text = font3_4.render(f'WAVE: {enemy_pool.wave_count}', False, (127, 127, 127))
    game_surface.blit(text, (0, 0))

    render_offset = [0, 0]
    if root.screen_shake > 0:
        render_offset = [randint(0, 8) - 4, randint(0, 8) - 4]
        root.screen_shake -= 1

    screen.blit(pygame.transform.scale_by(game_surface, window_size_mod), render_offset)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
