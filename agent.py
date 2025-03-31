import copy
import csv
import pickle
import re
import random

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

    # The qtable is a dictionary with keys that are tuples containing ClassNumbers
    def init_qtable(self):
        for course in self.course_list:
            self.qtable[ (course['ClassNumber']) ] = 0.0

    # Provide a list of all possible actions
    def get_all_possible_actions(self, state):
        all_actions = []

        # If the last course selected has required labs/ discussions, force the agent to select one
        if state[-1]['RequiredSections'] :
            for course in state[-1]['RequiredSections']:
                all_actions.append(course['ClassNumber'])
            return all_actions

        # Otherwise, return all courses not already in the schedule
        for course in self.course_list:
            if course['ClassNumber'] not in state:
                all_actions.append(course['ClassNumber'])

        all_actions.append('STOP')
        return all_actions

    def get_action(self, state):
        # using epilson greedy, pick the current best or random action
        true_epsilon = max(self.min_epsilon, self.epsilon)
        random_decimal = random.random()
        actions = self.get_all_possible_actions(state)

        if (random_decimal < true_epsilon):
            # Select random action
            random_action = random.choice(actions)
            return random_action
        else: # Select best action
            best_action = actions[0]
            state_tuple = tuple(state)
            max_qvalue = self.qtable[state_tuple + tuple(best_action)]

            for action in actions:
                qvalue = self.qtable[state_tuple + tuple(action)]
                if qvalue > max_qvalue:
                    max_qvalue = qvalue
                    best_action = action
            return best_action

    def step(self, state, action):
        # return next_state, reward
        next_state = state.append(action)
        reward = self.get_reward(self.request, state, action)
        return next_state, reward

    def get_reward(self, request, state, action):
        # return reward
        # placeholder
        return 5

    def update_qtable(self, old_state, action, reward, next_state):
        max_next_q = 0
        actions = self.get_all_possible_actions(next_state)
        for option in actions:
            if(tuple(next_state) + tuple(option)) not in self.qtable:
                self.qtable[(tuple(next_state) + tuple(option))] = 0
            if self.qtable[tuple(next_state) + tuple(option)] > max_next_q:
                max_next_q = self.qtable[tuple(next_state) + tuple(option)]

        sample = reward + max_next_q
        q_value = (1-self.alpha) * self.qtable[tuple(old_state) + tuple(action)] + (self.alpha*sample)
        self.qtable[tuple(old_state) + tuple(action)] = q_value

    # Return the total number of credits in the current state
    def get_num_credits(self, state):
        #implement
        num_credits = 0
        for course in state:
            num_credits += int(course['Units'])
        return num_credits

    # Training function based off of HW4 RL
    def train(self):
        for _ in self.episodes:
            condition = 'In Progress'
            state = []

            while condition == 'In Progress':
                action = self.get_action(state)

                if action == 'STOP' or self.get_num_credits(state) > 25: # Force the agent to stop after 25 credits
                    condition = 'Done'

                next_state, reward = self.step(state, action)

                old_state = copy.deepcopy(state)
                self.update_qtable(old_state, action, reward, next_state)
            # Update the epsilon value
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

        # Write the qtable to a file
        with open("","wb") as f:
            pickle.dump(self.qtable, f)
        print("Training complete! Q-table saved")
        return self.qtable

    def find_best_schedule(self):
        # use the qtable found during training to output the best schedule





