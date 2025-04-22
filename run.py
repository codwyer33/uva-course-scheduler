from agent import *
from parser import *

def main():
    episodes = 1000

    parser = Parser()
    course_dict = parser.parse_csv_into_dict('searchData.csv')
    course_dict = parser.remove_extra_courses(course_dict)
    parser.parse_times(course_dict)
    course_dict = parser.consolidate_lectures_and_discussions(course_dict)

    # for course in course_dict:
    #     print(course_dict[course])

    request = {'DesiredCourses': [ {'Mnemonic': 'CS', 'Number': '2100'},
                                    {'Mnemonic': 'CS', 'Number': '3710'}],
               'MaxCredits': 19,
               'MinCredits': 14,
               'Keywords': ['human', 'database', 'design', 'system'],
               'PreferredTimes' : ['Morning', 'Afternoon'],
               'LunchBreak': True
               }

    epsilon = 1.0
    min_epsilon = .01
    epsilon_decay = .99999
    gamma = .95
    alpha = .9

    agent = Agent(course_dict, episodes, request, epsilon, epsilon_decay, min_epsilon, gamma, alpha)
    agent.init_qtable()
    agent.train()
    agent.find_best_schedule()

    # for q in agent.qtable:
    #     print(q, agent.qtable[q])



main()