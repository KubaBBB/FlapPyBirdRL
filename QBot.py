
import numpy as np
import operator
from lazy_flappy import Environment


class QBot(object):
    """
    The Bot class that applies the Qlearning logic to Flappy bird game
    After every iteration (iteration = 1 game that ends with the bird dying) updates Q values
    """

    def __init__(self, max_attempts, packets):
        SCREENHEIGHT = 512
        BASEHEIGHT = 112
        MAX_VELOCITY = 10

        self.environment = Environment()
        self.iteration = 1
        self.upper_bounds = [SCREENHEIGHT - BASEHEIGHT, SCREENHEIGHT - BASEHEIGHT, SCREENHEIGHT - BASEHEIGHT, 50,
                             MAX_VELOCITY]
        self.lower_bounds = [0, 0, 0, -40, -9]

        self.packets_number = packets
        self.packets = self.apply_packets()

        self.epsilon = 0.95
        self.alpha = 0.6
        self.discount_factor = 0.7
        self.decrease_constant = 0.95
        self.max_attempts = max_attempts

        self.Q = {}

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
        done = [False, False]
        reward_sum = 0.0
        while not done[0]:
            action = self.pick_action(observation)
            new_observation, reward, done = self.environment.step(action)
            print(new_observation)
            new_observation = self.discretise(new_observation)
            self.update_knowledge(action, observation, new_observation, reward)
            observation = new_observation
            reward_sum += reward
            self.update_parameters()

            print(observation)
        return reward_sum

    def discretise(self, observation):
        discretised_values = []
        for idx, obs in enumerate(observation):
            discretised_values.append(np.clip(np.digitize(obs, self.packets[idx]), 1, self.packets_number[idx]))
        return tuple(discretised_values)

    def pick_action(self, observation):
        if np.random.random_sample() > self.epsilon and observation in self.Q and len(self.Q[observation]) > 0:
            return max(self.Q[observation].items(), key=operator.itemgetter(1))[0]
        else:
            if observation not in self.Q:
                self.Q[observation] = {}
            return self.environment.sample()

    def update_knowledge(self, action, observation, new_observation, reward):
        q_o_a = 0 if action not in self.Q[observation] else self.Q[observation][action]
        q_o_a_s1 = 0
        if new_observation in self.Q and len(self.Q[new_observation]) > 0:
            q_o_a_s1 = max(self.Q[new_observation].items(), key=operator.itemgetter(1))[1]
        q_new = ((1 - self.alpha) * q_o_a) + (self.alpha * (reward + (self.discount_factor * q_o_a_s1)))
        self.Q[observation][action] = q_new

    def update_parameters(self,):
        if self.iteration % (self.max_attempts / 10) == 0:
            self.epsilon *= self.decrease_constant
        self.alpha = np.clip(self.alpha, 0, 0.96)
        self.epsilon = np.clip(self.epsilon, 0.05, 1)
