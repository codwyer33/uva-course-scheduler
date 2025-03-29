import copy
import csv
import pickle
import re

class Agent:
    def __init__(self, course_list, episodes, request, epsilon, epsilon_decay, min_epsilon, gamma):
        self.course_list = course_list
        self.episodes = episodes
        self.qtable = {}
        self.request = request
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.gamma = gamma

    def are_times_overlapping(times1, times2):
        for t1 in times1:
            for t2 in times2:
                if t1['Day'] == t2['Day']:
                    if t1['StartTime'] > t2['StartTime'] and t1['EndTime'] < t2['EndTime']:
                        return False
                    if t2['StartTime'] > t1['StartTime'] and t2['EndTime'] < t1['EndTime']:
                        return False
        return True

    def init_qtable(self):
        for course in self.course_list:
            self.qtable[ course['ClassNumber'] ] = 0.0

    def get_all_possible_actions(self, state):
        # implement
        # provide a list of all possible actions

    def get_action(self, state):
        # implement
        # using epilson greedy, pick the current best or random action

    def step(self, state, action):
        # implement
        # return next_state, reward

    def get_reward(self, request, state, action):
        # implement
        # return reward

    def update_qtable(self, old_state, action, reward, next_state):
        # implement
        # return qtable

    # Return the total number of credits in the current state
    def get_num_credits(self, state):
        #implement

    # Training function based off of HW4 RL
    def train(self):
        for _ in self.episodes:
            condition = 'In Progress'
            while condition == 'In Progress':
                state = []
                action = self.get_action(state)

                if action == 'STOP' or self.get_num_credits(state) > 23:
                    condition = 'Done'

                next_state, reward = self.step(state, action)

                old_state = copy.deepcopy(state)
                self.qtable = self.update_qtable(old_state, action, reward, next_state)

        with open("","wb") as f:
            pickle.dump(self.qtable, f)
        print("Training complete! Q-table saved")
        return self.qtable

    def find_best_schedule(self):
        # use the qtable found during training to output the best schedule





