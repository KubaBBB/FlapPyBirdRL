import json
from QBot import QBot


def main():
    global_attempts = 4
    global_rewards = []
    global_rewards_counter = {}
    all_rewards = []
    attempts = 10000
    packets = [6, 6, 6, 6, 4]

    for _ in range(global_attempts):
        bot = QBot(attempts, packets)
        for _ in range(attempts):
            reward_sum = bot.attempt()
            all_rewards.append(reward_sum)
            print(reward_sum)
            # self.reward_counter[int(np.digitize(reward_sum, self.reward_bins, right=False))] += 1
    print("MAX" + max(all_rewards))


if __name__ == '__main__':
    main()
