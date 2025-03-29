import csv
import re

class Agent:
    def __init__(self, course_list, episodes, request):
        self.course_list = course_list
        self.episodes = episodes
        self.qtable = {}
        self.request = request

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

    # def train(episodes):
        # for _ in episodes:

    # def reward():




