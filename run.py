from agent import *
from parser import *

def main():
    episodes = 100

    parser = Parser()
    course_list = parser.parse_csv_into_dict('classes.csv')
    course_list = parser.remove_extra_courses(course_list)
    parser.parse_times(course_list)
    course_list = parser.consolidate_lectures_and_discussions(course_list)

    # for course in course_list:
    #     print(course)

    request = {'DesiredCourses': [{'Mnemonic': 'CS', 'Number': '7457'}, {'Mnemonic': 'CS', 'Number': '3205'}],
               'MaxCredits': 19,
               'MinCredits': 14,
               'Keywords': ['human', 'database', 'design', 'system']
               }

    epsilon =

    agent = Agent(course_list, episodes, request, epsilon, epsilon_decay, min_epsilon, gamma)
    agent.init_qtable()
    agent.train()

    # for q in agent.qtable:
    #     print(q, agent.qtable[q])



main()