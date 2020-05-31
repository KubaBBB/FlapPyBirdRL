import json
from QBot import QBot
import matplotlib.pyplot as plt
import numpy as np


class QVisualiser:
    def __init__(self, rewards_mean, rewards_std, rewards_counter, n, repeats):
        self.rewards_mean = rewards_mean
        self.rewards_std = rewards_std
        self.rewards_counter = rewards_counter[1:]
        self.N = n
        self.repeats = repeats

    def plot(self):
        x = range(1, len(self.rewards_mean) + 1)

        plt.plot(x, self.rewards_mean, color='red', linewidth=4, label='Reward mean')
        #plt.plot(x, self.rewards_mean + self.rewards_std, color='olive', linewidth=1, linestyle='dashed',
        #         label='Reward mean + std')
        #plt.plot(x, self.rewards_mean - self.rewards_std, color='olive', linewidth=1, linestyle='dashed',
        #         label='Reward mean - std')
        plt.legend(loc='lower right')
        plt.margins(x=0, y=0)
        plt.xlabel('Iterations')
        plt.ylabel('Rewards')
        plt.title(f'Q-Learning curve as moving mean with {self.N} window size')
        plt.show()


class QStatistician:
    def __init__(self, all_rewards, n):
        self.N = n
        self.all_rewards = self.apply_running_mean(all_rewards)

    def apply_running_mean(self, all_rewards):
        for i in range(len(all_rewards)):
            all_rewards[i] = self.running_mean(all_rewards[i])
        return all_rewards

    def running_mean(self, all_rewards):
        cumsum = np.cumsum(np.insert(all_rewards, 0, 0))
        return (cumsum[self.N:] - cumsum[:-self.N]) / float(self.N)

    def mean(self):
        return np.mean(self.all_rewards, axis=0)

    def std(self):
        return np.std(self.all_rewards, axis=0)

    def get_stats(self):
        return self.mean(), self.std()


def main():
    global_attempts = 1
    global_rewards = []
    global_rewards_counter = {}
    all_rewards = []
    attempts = 1500
    N = 100
    packets = [10, 10, 10, 10, 2]

    for att in range(global_attempts):
        print(att)
        Q = init_q(packets)
        bot = QBot(attempts, packets, Q)
        all_rewards = []
        for _ in range(attempts):
            reward_sum = bot.attempt()
            all_rewards.append(reward_sum)
            # self.reward_counter[int(np.digitize(reward_sum, self.reward_bins, right=False))] += 1
            global_rewards.append(all_rewards)
        bot.dump_q(f"q_{attempts}_{str(packets)}")

    statistician = QStatistician(global_rewards, N)
    rewards_mean, rewards_std = statistician.get_stats()

    visualizer = QVisualiser(rewards_mean, rewards_std,
                             list(global_rewards_counter.values()), N, attempts * global_attempts)
    visualizer.plot()


def init_q(packets):
    Q = {}
    for i in range(1, packets[0] + 1):
        for j in range(1, packets[1] + 1):
            for k in range(1, packets[2] + 1):
                for m in range(1, packets[3] + 1):
                    for l in range(1, packets[4] + 1):
                        Q[(i, j, k, m, l)] = {}
                        Q[(i, j, k, m, l)][0] = 1
                        Q[(i, j, k, m, l)][1] = -1
    return Q


if __name__ == '__main__':
    main()
