import random
import pickle
import pygame

SCREENWIDTH = 288
SCREENHEIGHT = 512
PIPE_GAP_SIZE = 100  # gap between upper and lower part of pipe
BASE_Y = SCREENHEIGHT * 0.79

IM_WIDTH = 0
IM_HEIGHT = 1
# image, Width, Height
PIPE = [52, 320]
PLAYER = [34, 24]
BASE = [336, 112]
BACKGROUND = [288, 512]


class Environment(object):
    def __init__(self):
        with open("assets/hitmasks_data.pkl", "rb") as input:
            self.hit_masks = pickle.load(input)

        self.player_x = int(SCREENWIDTH * 0.2)
        self.base_shift = BASE[IM_WIDTH] - BACKGROUND[IM_WIDTH]
        self.reset_environment()

    def reset_environment(self):
        self.score = 0
        self.player_y = int((SCREENHEIGHT - PLAYER[IM_HEIGHT]) / 2)
        self.base_x = 0
        self.player_shm_vals = {"val": 0, "dir": 1}
        self.movement_info = {"player_y": self.player_y + self.player_shm_vals["val"], "base_x": self.base_x}

        # get 2 new pipes to add to upperPipes lowerPipes list
        new_pipe1 = self.get_random_pipe()
        new_pipe2 = self.get_random_pipe()

        # list of upper pipes
        self.upper_pipes = [
            {"x": SCREENWIDTH - 80, "y": new_pipe1[0]["y"]},
            {"x": SCREENWIDTH - 80 + (SCREENWIDTH / 2), "y": new_pipe2[0]["y"]},
        ]

        # list of lowerpipe
        self.lower_pipes = [
            {"x": SCREENWIDTH - 80, "y": new_pipe1[1]["y"]},
            {"x": SCREENWIDTH - 80 + (SCREENWIDTH / 2), "y": new_pipe2[1]["y"]},
        ]

        self.pipe_vel_x = -4

        # player velocity, max velocity, downward accleration, accleration on flap
        self.player_vel_y = -9  # player's velocity along Y, default same as playerFlapped
        self.player_max_vel_y = 10  # max vel along Y, max descend speed
        self.player_min_vel_y = -8  # min vel along Y, max ascend speed
        self.player_acc_y = 1  # players downward accleration
        self.player_flap_acc = -9  # players speed on flapping
        self.player_flapped = False  # True when player flaps

        dist_x = -self.player_x + self.lower_pipes[0]["x"]

        observation = self.player_y, self.lower_pipes[0]["y"], self.upper_pipes[0]["y"], dist_x, self.player_vel_y

        return observation

    def restart(self):
        self.reset_environment()

    def step(self, action):
        dist_x = -self.player_x + self.lower_pipes[0]["x"]
        if dist_x > -30:
            closest_lower_pipe = self.lower_pipes[0]["y"]
            closest_upper_pipe = self.upper_pipes[0]["y"]
        else:
            closest_lower_pipe = self.lower_pipes[1]["y"]
            closest_upper_pipe = self.upper_pipes[1]["y"]

        need_refactor = 0

        if action:
            if self.player_y > 10 and self.player_vel_y > 0:
                self.player_vel_y = self.player_flap_acc
                self.player_flapped = True
            else:
                need_refactor = 1

        # check for crash here
        crash_test = self.check_crash({'x': self.player_x, 'y': self.player_y}, self.upper_pipes, self.lower_pipes)

        if crash_test[0]:
            observation = self.player_y, closest_lower_pipe, closest_upper_pipe, dist_x, self.player_vel_y

            if crash_test[1] or crash_test[2]:
                self.score -= 10
            return observation, self.score, crash_test, need_refactor

        # check for score
        player_mid_pos = self.player_x + PLAYER[IM_WIDTH] / 2
        for pipe in self.upper_pipes:
            pipe_mid_pos = pipe['x'] + PIPE[IM_WIDTH] / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                self.score += 1

        # player's movement
        if self.player_vel_y < self.player_max_vel_y and not self.player_flapped:
            self.player_vel_y += self.player_acc_y

        self.player_flapped = False

        self.player_y += min(self.player_vel_y, BASE_Y - self.player_y - PLAYER[IM_HEIGHT])

        # move pipes to left
        for uPipe, lPipe in zip(self.upper_pipes, self.lower_pipes):
            uPipe['x'] += self.pipe_vel_x
            lPipe['x'] += self.pipe_vel_x

        # add new pipe when first pipe is about to touch left of screen
        if 0 < self.upper_pipes[0]['x'] < 5:
            new_pipe = self.get_random_pipe()
            self.upper_pipes.append(new_pipe[0])
            self.lower_pipes.append(new_pipe[1])

        # remove first pipe if its out of the screen
        if self.upper_pipes[0]['x'] < -PIPE[IM_WIDTH]:
            self.upper_pipes.pop(0)
            self.lower_pipes.pop(0)

        dist_x = -self.player_x + self.lower_pipes[0]["x"]
        if dist_x > -30:
            closest_lower_pipe = self.lower_pipes[0]["y"]
            closest_upper_pipe = self.upper_pipes[0]["y"]
        else:
            closest_lower_pipe = self.lower_pipes[1]["y"]
            closest_upper_pipe = self.upper_pipes[1]["y"]

        observation = self.player_y, closest_lower_pipe, closest_upper_pipe, dist_x, self.player_vel_y

        return observation, self.score, crash_test, need_refactor

    def sample(self):
        return random.randint(0, 1)

    def check_crash(self, player, upper_pipes, lower_pipes):
        player["w"] = PLAYER[IM_WIDTH]
        player["h"] = PLAYER[IM_HEIGHT]

        # if player crashes into ground
        if player['y'] + player['h'] >= BASE_Y - 1:
            return [True, True, False]
        else:

            player_rect = pygame.Rect(player['x'], player['y'], player['w'], player['h'])
            pipe_w = PIPE[IM_WIDTH]
            pipe_h = PIPE[IM_HEIGHT]

            for uPipe, lPipe in zip(upper_pipes[:2], lower_pipes[:2]):
                # upper and lower pipe rects
                u_pipe_rect = pygame.Rect(uPipe['x'], uPipe['y'], pipe_w, pipe_h)
                l_pipe_rect = pygame.Rect(lPipe['x'], lPipe['y'], pipe_w, pipe_h)

                # player and upper/lower pipe hitmasks
                p_hit_mask = self.hit_masks['player'][0]
                u_hit_mask = self.hit_masks['pipe'][0]
                l_hit_mask = self.hit_masks['pipe'][1]

                # if bird collided with upipe or lpipe
                u_collide = self.pixel_collision(player_rect, u_pipe_rect, p_hit_mask, u_hit_mask)
                l_collide = self.pixel_collision(player_rect, l_pipe_rect, p_hit_mask, l_hit_mask)

                if u_collide or l_collide:
                    return [True, False, u_collide]

        return [False, False, False]

    def player_shm(self, player_shm):
        """oscillates the value of playerShm['val'] between 8 and -8"""
        if abs(player_shm['val']) == 8:
            player_shm['dir'] *= -1

        if player_shm['dir'] == 1:
            player_shm['val'] += 1
        else:
            player_shm['val'] -= 1

    def get_random_pipe(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gap_y = random.randrange(0, int(BASE_Y * 0.6 - PIPE_GAP_SIZE))
        gap_y += int(BASE_Y * 0.2)
        pipe_height = PIPE[IM_HEIGHT]
        pipe_x = SCREENWIDTH + 10

        return [
            {'x': pipe_x, 'y': gap_y - pipe_height},  # upper pipe
            {'x': pipe_x, 'y': gap_y + PIPE_GAP_SIZE + random.randrange(45, 95)}  # lower pipe
        ]

    def pixel_collision(self, rect1, rect2, hitmask1, hitmask2):
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
