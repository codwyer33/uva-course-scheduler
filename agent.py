import copy
import csv
import pickle
import re
import random

class Agent:
    def __init__(self, course_list, episodes, request, epsilon, epsilon_decay, min_epsilon, gamma, alpha):
        self.course_list = course_list
        self.episodes = episodes
        self.qtable = {}
        self.request = request
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.gamma = gamma
        self.alpha = alpha

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
        if state and len(state) > 0:
            for course in self.course_list:
                if course['ClassNumber'] == state[-1] and 'RequiredSections' in course:
                    for req_course in course['RequiredSections']:
                        all_actions.append(req_course['ClassNumber'])
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
            if tuple(sorted(state_tuple + (best_action,))) not in self.qtable: #init if not in table
                self.qtable[tuple(sorted(state_tuple + (best_action,)))] = 0

            max_qvalue = self.qtable[tuple(sorted(state_tuple + (best_action,)))]

            for action in actions:
                if tuple(sorted(state_tuple + (action,))) not in self.qtable: #init if not in table
                    self.qtable[tuple(sorted(state_tuple + (action,)))] = 0

                qvalue = self.qtable[tuple(sorted(state_tuple + (action,)))]
                if qvalue > max_qvalue:
                    max_qvalue = qvalue
                    best_action = action
            return best_action

    def step(self, state, action):
        # return next_state, reward
        next_state = state + [action]
        reward = self.get_reward(self.request, state, action)
        return next_state, reward

    def get_reward(self, request, state, action):
        # return reward
        # placeholder
        reward = 0
        for desired_course in request['DesiredCourses']:
            for selected_course in state:
                for course in self.course_list:
                    if course['ClassNumber'] == selected_course:
                        if course['Mnemonic'] == desired_course['Mnemonic'] and course['Number'] == desired_course['Number']:
                            reward += 5

        # if self.get_num_credits(state + [action]) > request['MinCredits'] :
        #     if self.get_num_credits(state + [action]) < request['MaxCredits']:
        #         reward += 5
        #     else:
        #         reward -= 10
        return reward

    def update_qtable(self, old_state, action, reward, next_state):
        max_next_q = 0
        actions = self.get_all_possible_actions(next_state)
        for option in actions:
            if(tuple(next_state) + tuple(option)) not in self.qtable:
                self.qtable[tuple(sorted((tuple(next_state) + (option, ))))] = 0
            if self.qtable[tuple(sorted(tuple(next_state) + (option, )))] > max_next_q:
                max_next_q = self.qtable[tuple(sorted(tuple(next_state) + (option, )))]

        sample = reward + max_next_q

        if tuple(sorted(tuple(old_state) + (action,))) not in self.qtable:
            self.qtable[tuple(sorted(tuple(old_state) + (action,)))] = 0

        # print(sample, reward, max_next_q, self.qtable[tuple(sorted(tuple(old_state) + (action,)))])

        q_value = (1-self.alpha) * self.qtable[tuple(sorted(tuple(old_state) + (action,)))] + (self.alpha*sample)
        self.qtable[tuple(sorted(tuple(old_state) + (action, )))] = q_value
        # print("update ", q_value, tuple(sorted(tuple(old_state) + (action, ))))

    # Return the total number of credits in the current state
    def get_num_credits(self, state):
        num_credits = 0
        for class_number in state:
            for course in self.course_list:
                if course['ClassNumber'] == class_number:
                    if "-" in course['Units']: # simplifies dealing with courses that have a range of units, ie "1-3"
                        num_credits += 1
                    else:
                        num_credits += int(course['Units'])
        return num_credits

    # Training function based off of HW4 RL
    def train(self):
        for _ in range(self.episodes):
            condition = 'In Progress'
            state = []
            # print("New episode")
            while condition == 'In Progress':
                action = self.get_action(state)
                # print("a", action)

                if action == 'STOP' or self.get_num_credits(state) > 15: # Force the agent to stop after 25 credits
                    condition = 'Done'

                next_state, reward = self.step(state, action)
                old_state = copy.deepcopy(state)
                state = next_state
                self.update_qtable(old_state, action, reward, next_state)
            # Update the epsilon value
            print(state, self.get_reward(self.request, state, 'STOP'))
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

        # Write the qtable to a file
        with open("qtable.pkl","wb") as f:
            pickle.dump(self.qtable, f)
        print("Training complete, qtable saved")

        # for q in self.qtable:
        #     if self.qtable[q] != 0 and self.qtable[q] != 1:
        #         print(q, self.qtable[q])
        return self.qtable

    # def find_best_schedule(self):
        # use the qtable found during training to output the best schedule





