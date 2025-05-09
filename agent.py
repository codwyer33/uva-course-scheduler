import copy
import csv
import pickle
import re
import random
import matplotlib.pyplot as plt

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

    def are_times_overlapping(self, times1, times2):
        for t1 in times1:
            for t2 in times2:
                if t1['Day'] == t2['Day']:  # Check same day
                    if not (t1['EndTime'] <= t2['StartTime'] or t2['EndTime'] <= t1['StartTime']):
                        return True
        return False

    # The qtable is a dictionary with keys that are tuples containing ClassNumbers
    def init_qtable(self):
        for course in self.course_list:
            if course in self.request['DesiredCourses']:
                self.qtable[course] = 50
            else:
                self.qtable[course] = 0.0

    # Provide a list of all possible actions
    def get_all_possible_actions(self, state):
        all_actions = []

        # If the last course selected has required labs/ discussions, force the agent to select one
        if state and len(state) > 0 and state[-1] != 'STOP':
            # print(state, self.course_list[state[-1]])
            if 'RequiredSections' in self.course_list[state[-1]]:
                # print("reaching a course with required sections")
                all_actions = self.course_list[state[-1]]['RequiredSections']
                return all_actions

            # if course == state[-1] and 'RequiredSections' in self.course_list[course]:
            #         all_actions = self.course_list['RequiredSections']
            #         return all_actions

        # Otherwise, return all courses that are not duplicates, don't overlap, and not labs/discussions
        filtered_actions = []
        for k2 in self.course_list: # Restrict agent from choosing 2 courses that are duplicates
            is_duplicate_or_overlaps = False
            for k1 in state:
                if self.are_keys_the_same_course(k1, k2):
                    is_duplicate_or_overlaps = True
                    break
                elif k1 != 'STOP' and self.are_times_overlapping(self.course_list[k1]['Times'], self.course_list[k2]['Times']): # Eliminate overlapping times
                    is_duplicate_or_overlaps = True
                    break
            if not is_duplicate_or_overlaps and self.course_list[k2]['Type'] == 'Lecture':
                filtered_actions.append(k2)

        filtered_actions.append('STOP')
        return filtered_actions
    
    def get_random_cs_courses(self, state, actionList):
        csActions = []
        for key in self.course_list:
            if(self.course_list[key]['Mnemonic'] == 'CS'):
                csActions.append(key)
        return csActions




    def get_action(self, state, chooseBestAction, actionsList):
        # using epilson greedy, pick the current best or random action
        true_epsilon = max(self.min_epsilon, self.epsilon)

        if actionsList != "":
            actions = actionsList
        else:
            actions = self.get_all_possible_actions(state)
        # Select random action
        if random.random() < true_epsilon and not chooseBestAction:
            # if random.random() < .05: #Force a higher likelihood of choosing stop
            #     return 'STOP'
            if random.random() < 0.1:
                csActions = self.get_random_cs_courses(state, actions)
                return random.choice(csActions)
            else:
                return random.choice(actions)
        else: # Select best action
            best_action = actions[0]
            state_key = tuple(state)

            for action in actions:
                if (state_key + (action,)) not in self.qtable: #init if not in table
                    self.qtable[state_key + (action,)] = 0

            max_qvalue = -100000
            best_action = action[0]

            for action in actions:
                qvalue = self.qtable[state_key + (action,)]
                if qvalue > max_qvalue:
                    max_qvalue = qvalue
                    best_action = action
            return best_action

    def step(self, state, action):
        # return next_state, reward
        next_state = state + [action]
        reward = self.get_reward(self.request, state, action)
        return next_state, reward

    def are_keys_the_same_course(self, k1, k2):
        if k1 == 'STOP' or k2 == 'STOP':
            return False
        if self.course_list[k1]['Mnemonic'] == self.course_list[k2]['Mnemonic'] and self.course_list[k1]['Number'] == self.course_list[k2]['Number'] :
            return True
        return False

    def get_reward(self, request, state, action):
        # return reward
        reward = 0
        numberOfDesiredCourses = 0
        for desired_course in request['DesiredCourses']:
            for selected_course in state + [action]:
                if selected_course in self.course_list:
                    if self.course_list[selected_course]['Mnemonic'] == desired_course['Mnemonic']:
                        reward += 5
                    if self.course_list[selected_course]['Mnemonic'] == desired_course['Mnemonic'] and self.course_list[selected_course]['Number'] == desired_course['Number']:
                        # print("reward +30")
                        numberOfDesiredCourses += 1
                        reward += 70
                        break
        
        if numberOfDesiredCourses >= len(request['DesiredCourses']):
            reward += 80

        for word in request['Keywords']:
            for class_number in state + [action]:
                if class_number in self.course_list:
                    if word in self.course_list[class_number]['Description']:
                            reward += 5

        # if self.get_num_credits(state + [action]) > request['MinCredits'] :
        #     reward += 5
        # if self.get_num_credits(state + [action]) > request['MaxCredits']:
        #     reward -= 100

        # if self.get_num_credits(state + [action]) > request['MinCredits'] :
        #     if self.get_num_credits(state + [action]) < request['MaxCredits']:
        #         reward += 100

        #time priorities
        if 'Morning' in request['PreferredTimes']:
            for class_number in state + [action]:
                if class_number in self.course_list:
                    for day in self.course_list[class_number]['Times']:
                        if day['EndTime'] <= 720:
                            # print("reward +3 morning")
                            reward += 2
        
        if 'Afternoon' in request['PreferredTimes']:
            for class_number in state + [action]:
                if class_number in self.course_list:
                    for day in self.course_list[class_number]['Times']:
                        if day['StartTime'] >= 720 and day['EndTime'] <= 1020:
                            # print("reward +3 afternoon")
                            reward += 2

        if 'Evening' in request['PreferredTimes']:
            for class_number in state + [action]:
                if class_number in self.course_list:
                    for day in self.course_list[class_number]['Times']:
                        if day['StartTime'] >= 1020:
                            # print("reward +3 evening")
                            reward += 2

        if request['LunchBreak']:
            lunchLate = True
            lunchEarly = True
            for class_number in state + [action]:
                if class_number in self.course_list:
                    for day in self.course_list[class_number]['Times']:
                        if day['StartTime'] <= 840 and day['EndTime'] >= 780:
                            lunchLate = False
                        if day['StartTime'] <= 780 and day['EndTime'] >= 720:
                            lunchLate = False
            if lunchLate or lunchEarly:
                # print("reward +20 lunch")
                reward += 10

        # if action == 'STOP':
        #     reward += 15

        return reward

        # for s in state:
        #     for z in state:
        #         if self.are_keys_the_same_course(s, z):
        #             reward -= 100

        # if self.get_num_credits(state + [action]) > request['MinCredits'] :
        #     if self.get_num_credits(state + [action]) < request['MaxCredits']:
        #         reward += 5
        #     else:
        #         reward -= 10


    def update_qtable(self, old_state, action, reward, next_state):
        max_next_q = 0
        actions = self.get_all_possible_actions(next_state)
        for option in actions:
            key = tuple(next_state) + (option,)
            if key not in self.qtable:
                self.qtable[key] = 0 # Init if missing
            max_next_q = max(max_next_q, self.qtable[key])

            # if(tuple(next_state) + tuple(option)) not in self.qtable:
            #     self.qtable[tuple(sorted((tuple(next_state) + (option, ))))] = 0
            # if self.qtable[tuple(sorted(tuple(next_state) + (option, )))] > max_next_q:
            #     max_next_q = self.qtable[tuple(sorted(tuple(next_state) + (option, )))]

        sample = reward + (max_next_q * self.gamma)
        old_key = tuple(old_state) + (action,)
        if old_key not in self.qtable:
            self.qtable[old_key] = 0

        # print(sample, reward, max_next_q, self.qtable[tuple(sorted(tuple(old_state) + (action,)))])

        q_value = (1-self.alpha) * self.qtable[old_key] + (self.alpha*sample)
        self.qtable[old_key] = q_value
        # print("update ", q_value, tuple(sorted(tuple(old_state) + (action, ))))

    # Return the total number of credits in the current state
    def get_num_credits(self, state):
        num_credits = 0
        for class_number in state:
            if class_number not in self.course_list:
                continue
            if "-" in self.course_list[class_number]['Units']: # simplifies dealing with courses that have a range of units, ie "1-3"
                num_credits += 1
            else:
                num_credits += float((self.course_list[class_number]['Units']))

        return num_credits

    # Training function based off of HW4 RL
    def train(self):
        training_progress = []
        for _ in range(self.episodes):
            condition = 'In Progress'
            state = []
            print("Episode", _)
            avg_reward = []
            while condition == 'In Progress':
                action = self.get_action(state, False, "")
                # print("a", action)

                if 'STOP' in state or self.get_num_credits(state) >= self.request['MaxCredits']: # Force the agent to stop above the desired max
                    condition = 'Done'

                next_state, reward = self.step(state, action)
                avg_reward.append(reward)
                old_state = copy.deepcopy(state)
                state = next_state
                self.update_qtable(old_state, action, reward, next_state)

            # Update the epsilon value
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            print(self.epsilon)
            training_progress.append(sum(avg_reward) / len(avg_reward))

            # print("Schedule - Reward:", self.get_reward(self.request, state, ""), "Credits:",self.get_num_credits(state))
            # for s in state:
            #     if s != 'STOP':
            #         course = self.course_list[s]
            #         print(course['Mnemonic'], course['Number'], course['Title'], course['Days'])

            # print(state, self.get_reward(self.request, state, ''), self.epsilon)

        # for q in self.qtable:
        #     if self.qtable[q] != 0 and self.qtable[q] != 1:
        #         print(q, self.qtable[q])

        # Visualize training progress
        plt.scatter(range(len(training_progress)), training_progress, color='blue', marker='o')
        plt.xlabel('Time')
        plt.ylabel('Reward')
        plt.title('Training Progress')
        plt.grid(True)
        plt.show()

        return training_progress

    def find_best_schedule(self, number_of_schedules):
        # use the qtable found during training to output the best schedule
        print("Finding Best Schedule(s)")
        restricted_states = []
        eval_reward_array = []

        # Repeatedly find a good schedule
        for i in range(number_of_schedules):
            condition = 'In Progress'
            state = []
            while condition == 'In Progress':
                actions = self.get_all_possible_actions(state)
                allowed_actions = set(actions) - set(restricted_states)

                action = self.get_action(state, True, list(allowed_actions))

                # To generate unique schedules, prevent a course from being chosen again unless it was user-requested
                if action != 'STOP':
                    isCourseDesired = False
                    for k in self.request['DesiredCourses']:
                        if self.course_list[action]['Mnemonic'] == k['Mnemonic'] and self.course_list[action]['Number'] == k['Number']:
                            isCourseDesired = True
                            continue
                    if not isCourseDesired:
                        restricted_states.append(action)

                old_state = copy.deepcopy(state)
                next_state, reward = self.step(state, action)
                state = next_state

                # print(self.get_num_credits(state))
                if action == 'STOP': # Force the agent to stop after 25 credits
                    condition = 'Done'
                elif self.get_num_credits(state) > self.request['MaxCredits']: # if we went over the limit, backtrack and finish
                    condition = 'Done'
                    state = old_state

            print()
            print("Schedule - Reward:", self.get_reward(self.request, state, ""), "Credits:",self.get_num_credits(state))
            eval_reward_array.append(self.get_reward(self.request, state, ""))
            for s in state:
                if s != 'STOP':
                    course = self.course_list[s]
                    print(course['Mnemonic'], course['Number'], course['Title'], course['Days'])

        return eval_reward_array





