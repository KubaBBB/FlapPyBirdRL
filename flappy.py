from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *
from assets import get_assets

from json import load
from ast import literal_eval
import QBot

FPS = 60
SCREENWIDTH = 288
SCREENHEIGHT = 512
PIPE_GAP_SIZE = 100  # gap between upper and lower part of pipe
BASE_Y = SCREENHEIGHT * 0.79
IMAGES, SOUNDS, HIT_MASKS = {}, {}, {}


def main():
    global SCREEN, FPS_CLOCK, IMAGES, SOUNDS, HIT_MASKS, Q, QBOT
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')

    IMAGES, SOUNDS, HIT_MASKS = get_assets()

    Q = read_q("q_1500_[10, 10, 10, 10, 2]")
    QBOT = QBot.QBot(0, [10, 10, 10, 10, 2], Q)
    while True:
        movement_info = show_welcome_animation()
        crash_info = main_game(movement_info)
        show_game_over_screen(crash_info)


def show_welcome_animation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    player_index_gen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration

    player_x = int(SCREENWIDTH * 0.2)
    player_y = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    base_x = 0
    # amount by which base can maximum shift to left
    base_shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    player_shm_vals = {'val': 0, 'dir': 1}

    # adjust player_y, playerIndex, base_x
    base_x = -((-base_x + 4) % base_shift)
    player_shm(player_shm_vals)

    # draw sprites
    SCREEN.blit(IMAGES['background'], (0, 0))
    SCREEN.blit(IMAGES['player'][0],
                (player_x, player_y + player_shm_vals['val']))
    SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))

    pygame.display.update()
    FPS_CLOCK.tick(FPS)

    SOUNDS['wing'].play()
    return {
        'player_y': player_y + player_shm_vals['val'],
        'base_x': base_x,
        'player_index_gen': player_index_gen,
    }


def main_game(movement_info):
    score = player_index = loop_iter = 0
    player_index_gen = movement_info['player_index_gen']
    player_x, player_y = int(SCREENWIDTH * 0.2), movement_info['player_y']

    base_x = movement_info['base_x']
    base_shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upper_pipes lower_pipes list
    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    # list of upper pipes
    upper_pipes = [
        {'x': SCREENWIDTH - 80, 'y': new_pipe1[0]['y']},
        {'x': SCREENWIDTH - 80 + (SCREENWIDTH / 2), 'y': new_pipe2[0]['y']},
    ]

    # list of lowerpipe
    lower_pipes = [
        {'x': SCREENWIDTH - 80, 'y': new_pipe1[1]['y']},
        {'x': SCREENWIDTH - 80 + (SCREENWIDTH / 2), 'y': new_pipe2[1]['y']},
    ]

    pipe_vel_x = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    player_vel_y = -9  # player's velocity along Y, default same as player_flapped
    player_max_vel_y = 10  # max vel along Y, max descend speed
    player_acc_y = 1  # players downward accleration
    player_rot = 45  # player's rotation
    player_vel_rot = 3  # angular speed
    player_rot_thr = 20  # rotation threshold
    player_flap_acc = -9  # players speed on flapping
    player_flapped = False  # True when player flaps

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > -2 * IMAGES['player'][0].get_height():
                #    player_vel_y = player_flap_acc
                 #   player_flapped = True
                    SOUNDS['wing'].play()

        if player_y > 10 and player_vel_y > 0:

            dist_x = -player_x + lower_pipes[0]["x"]
            if dist_x > -30:
                closest_lower_pipe = lower_pipes[0]["y"]
                closest_upper_pipe = upper_pipes[0]["y"]
            else:
                closest_lower_pipe = lower_pipes[1]["y"]
                closest_upper_pipe = upper_pipes[1]["y"]

            observation = player_y, closest_lower_pipe, closest_upper_pipe, dist_x, player_vel_y
            action = QBOT.act(observation)
            if action != '0':
                print("IN ACTION")
                player_vel_y = player_flap_acc
                player_flapped = True
                SOUNDS['wing'].play()

        # check for crash here
        crash_test = check_crash({'x': player_x, 'y': player_y, 'index': player_index},
                                 upper_pipes, lower_pipes)
        if crash_test[0]:
            return {
                'y': player_y,
                'groundCrash': crash_test[1],
                'base_x': base_x,
                'upper_pipes': upper_pipes,
                'lower_pipes': lower_pipes,
                'score': score,
                'player_vel_y': player_vel_y,
                'player_rot': player_rot
            }

        # check for score
        player_mid_pos = player_x + IMAGES['player'][0].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                SOUNDS['point'].play()

        # player_index base_x change
        if (loop_iter + 1) % 3 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 100) % base_shift)

        # rotate the player
        if player_rot > -90:
            player_rot -= player_vel_rot

        # player's movement
        if player_vel_y < player_max_vel_y and not player_flapped:
            player_vel_y += player_acc_y
        if player_flapped:
            # more rotation to cover the threshold (calculated in visible rotation)
            player_rot = 45
        player_flapped = False

        player_height = IMAGES['player'][0].get_height()
        player_y += min(player_vel_y, BASE_Y - player_y - player_height)

        # move pipes to left
        for uPipe, lPipe in zip(upper_pipes, lower_pipes):
            uPipe['x'] += pipe_vel_x
            lPipe['x'] += pipe_vel_x

        # add new pipe when first pipe is about to touch left of screen
        if len(upper_pipes) > 0 and 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # remove first pipe if its out of the screen
        if len(upper_pipes) > 0 and upper_pipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))
        # print score so player overlaps the score
        show_score(score)

        # Player rotation has a threshold
        visible_rot = player_rot_thr
        if player_rot <= player_rot_thr:
            visible_rot = player_rot

        player_surface = pygame.transform.rotate(IMAGES['player'][player_index], visible_rot)
        SCREEN.blit(player_surface, (player_x, player_y))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def show_game_over_screen(crash_info):
    """crashes the player down ans shows gameover image"""
    score = crash_info['score']
    player_x = SCREENWIDTH * 0.2
    player_y = crash_info['y']
    player_height = IMAGES['player'][0].get_height()
    player_vel_y = crash_info['player_vel_y']
    player_acc_y = 2
    player_rot = crash_info['player_rot']
    player_vel_rot = 7

    base_x = crash_info['base_x']

    upper_pipes, lower_pipes = crash_info['upper_pipes'], crash_info['lower_pipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crash_info['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y + player_height >= BASE_Y - 1:
                    return

        # player y shift
        if player_y + player_height < BASE_Y - 1:
            player_y += min(player_vel_y, BASE_Y - player_y - player_height)

        # player velocity change
        if player_vel_y < 15:
            player_vel_y += player_acc_y

        # rotate only when it's a pipe crash
        if not crash_info['groundCrash']:
            if player_rot > -90:
                player_rot -= player_vel_rot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (base_x, BASE_Y))
        show_score(score)

        player_surface = pygame.transform.rotate(IMAGES['player'][1], player_rot)
        SCREEN.blit(player_surface, (player_x, player_y))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPS_CLOCK.tick(FPS)
        pygame.display.update()


def player_shm(player_shm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(player_shm['val']) == 8:
        player_shm['dir'] *= -1

    if player_shm['dir'] == 1:
        player_shm['val'] += 1
    else:
        player_shm['val'] -= 1


def get_random_pipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gap_y = random.randrange(0, int(BASE_Y * 0.6 - PIPE_GAP_SIZE))
    gap_y += int(BASE_Y * 0.2)
    pipe_height = IMAGES['pipe'][0].get_height()
    pipe_x = SCREENWIDTH + 10

    return [
        {'x': pipe_x, 'y': gap_y - pipe_height},  # upper pipe
        {'x': pipe_x, 'y': gap_y + PIPE_GAP_SIZE + random.randrange(45, 95)}  # lower pipe
    ]


def show_score(score):
    """displays score in center of screen"""
    score_digits = [int(x) for x in list(str(score))]
    total_width = 0  # total width of all numbers to be printed

    for digit in score_digits:
        total_width += IMAGES['numbers'][digit].get_width()

    x_offset = (SCREENWIDTH - total_width) / 2

    for digit in score_digits:
        SCREEN.blit(IMAGES['numbers'][digit], (x_offset, SCREENHEIGHT * 0.1))
        x_offset += IMAGES['numbers'][digit].get_width()


def check_crash(player, upper_pipes, lower_pipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASE_Y - 1:
        return [True, True]
    else:

        player_rect = pygame.Rect(player['x'], player['y'], player['w'], player['h'])
        pipe_w = IMAGES['pipe'][0].get_width()
        pipe_h = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upper_pipes, lower_pipes):
            # upper and lower pipe rects
            u_pipe_rect = pygame.Rect(uPipe['x'], uPipe['y'], pipe_w, pipe_h)
            l_pipe_rect = pygame.Rect(lPipe['x'], lPipe['y'], pipe_w, pipe_h)

            # player and upper/lower pipe hitmasks
            p_hit_mask = HIT_MASKS['player'][pi]
            u_hit_mask = HIT_MASKS['pipe'][0]
            l_hit_mask = HIT_MASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            u_collide = pixel_collision(player_rect, u_pipe_rect, p_hit_mask, u_hit_mask)
            l_collide = pixel_collision(player_rect, l_pipe_rect, p_hit_mask, l_hit_mask)

            if u_collide or l_collide:
                return [True, False]

    return [False, False]


def pixel_collision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def read_q(filename):
    with open(f'trained_q/{filename}.json', 'r') as f: obj = load(f)

    return {literal_eval(k): v for k, v in obj.items()}


if __name__ == '__main__':
    main()
