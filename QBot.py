from json import dump
import numpy as np
import operator
from lazy_flappy import Environment


class QBot(object):
    """
    The Bot class that applies the Qlearning logic to Flappy bird game
    After every iteration (iteration = 1 game that ends with the bird dying) updates Q values
    """

    def __init__(self, max_attempts, packets, Q):
        SCREENHEIGHT = 512
        BASEHEIGHT = 112
        MAX_VELOCITY = 10
        MIN_VELOCITY = -9
        SCREEN_UP_EDGE = 0

        self.environment = Environment()
        self.iteration = 1
        self.upper_bounds = [SCREENHEIGHT - BASEHEIGHT, SCREENHEIGHT - BASEHEIGHT, SCREENHEIGHT - BASEHEIGHT, 50,
                             MAX_VELOCITY]
        self.lower_bounds = [SCREEN_UP_EDGE, SCREEN_UP_EDGE, SCREEN_UP_EDGE, -40, MIN_VELOCITY]

        self.packets_number = packets
        self.packets = self.apply_packets()

        self.epsilon = 0.3
        self.alpha = 0.2
        self.discount_factor = 0.7
        self.decrease_constant = 0.75
        self.max_attempts = max_attempts

        self.Q = Q
        self.last_up_action = {'obs': 0, 'new_obs': 0}
        self.last_up_action_iters = 0

        self.all_rewards = []
        # self.reward_counter = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        # self.reward_bins = [200, 300, 400, 500]

    def apply_packets(self):
        packets = []

        for lb, ub, pn in zip(self.lower_bounds, self.upper_bounds, self.packets_number):
            packets.append(np.linspace(lb, ub, num=pn + 1))
        return packets

    def attempt(self):
        observation = self.discretise(self.environment.reset_environment())
        done = [False, False, False]
        reward_sum = 0.0
        while not done[0]:
            action = self.pick_action(observation)
            new_observation, reward, done, need_refactor = self.environment.step(action)
            new_observation = self.discretise(new_observation)
            self.update_knowledge(action and not need_refactor, observation, new_observation, reward)
            observation = new_observation
            reward_sum += reward
            self.update_parameters()
        if done[2] and self.last_up_action_iters < 10:  # fail by press SPACE near up pipe
            self.update_knowledge(1, self.last_up_action['obs'], self.last_up_action['new_obs'], -10)
        return reward_sum

    def discretise(self, observation):
        discretised_values = []
        for idx, obs in enumerate(observation):
            discretised_values.append(np.clip(np.digitize(obs, self.packets[idx]), 1, self.packets_number[idx]))
        return tuple(discretised_values)

    def pick_action(self, observation):
        if np.random.random_sample() > self.epsilon:
            return max(self.Q[observation].items(), key=operator.itemgetter(1))[0]
        else:
            return self.environment.sample()

    def act(self, observation):
        discretised_obs = self.discretise(observation)
        print(discretised_obs)
        print(self.Q[discretised_obs].items())
        return max(self.Q[discretised_obs].items(), key=operator.itemgetter(1))[0]

    def update_knowledge(self, action, observation, new_observation, reward):
        q_o_a = self.Q[observation][action]
        q_o_a_s1 = max(self.Q[new_observation].items(), key=operator.itemgetter(1))[1]

        q_new = ((1 - self.alpha) * q_o_a) + (self.alpha * (reward + (self.discount_factor * q_o_a_s1)))
        self.Q[observation][action] = q_new

        if action == 1:
            self.last_up_action_iters = 0
            self.last_up_action['obs'] = observation
            self.last_up_action['new_obs'] = new_observation
        else:
            self.last_up_action_iters += 1

    def update_parameters(self):
        self.iteration += 1
        if self.iteration % (self.max_attempts / 10) == 0 and self.iteration < self.max_attempts / 2:
            self.epsilon *= self.decrease_constant
        self.alpha = np.clip(self.alpha, 0, 0.96)
        self.epsilon = np.clip(self.epsilon, 0.05, 1)

    def dump_q(self, name):
        """
        Dump the qvalues to the JSON file
        """
        file = open(f"trained_q/{name}.json", "w")
        dump({str(k): v for k, v in self.Q.items()}, file)
        file.close()
        print("Q-values updated on local file.")

