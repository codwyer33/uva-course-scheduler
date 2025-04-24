from agent import *
from parser import *
from parse_prereq import *

def test(epsilon = 1.0, min_epsilon = .05, epsilon_decay = .997, gamma = .5, alpha = .5):
    request = {'DesiredCourses': [ {'Mnemonic': 'CS', 'Number': '3100'},
                                   {'Mnemonic': 'CS', 'Number': '3710'}],
               'MaxCredits': 19,
               'MinCredits': 14,
               'Keywords': ['human', 'database', 'design', 'system'],
               'NumberOfSchedules': 3,
               'PreferredTimes' : ['Morning', 'Afternoon'],
               'LunchBreak': True,
               'AdditionalCoursesTaken': {'CS 1100': 'A', 'APMA 1110': 'A'} # Add courses received through HS or transfer credit, not on main part of transcript
               }
    episodes = 1000

    # Parse Lou's List csv into dictionary
    parser = Parser()
    course_dict = parser.parse_csv_into_dict('searchData.csv')
    course_dict = parser.remove_extra_courses(course_dict)
    parser.parse_times(course_dict)
    course_dict = parser.consolidate_lectures_and_discussions(course_dict)

    # Add prerequisites to CS courses from a manually assembled dictionary
    course_dict = parser.add_prereqs(course_dict)

    # Assemble a list of courses this user has taken, from their transcript and additional entries in the request
    # courses_taken = parse_transcript_into_json("transcript.pdf")
    # for key in request['AdditionalCoursesTaken']:
    #     courses_taken[key] = request['AdditionalCoursesTaken'][key]

    # Use a hard-coded list for testing
    courses_taken = {'APMA 2120': 'A', 'CS 2100': 'A', 'CS 2120': 'A',
                          'CS 3140': 'A', 'CS 1100': 'A', 'APMA 1110': 'A'}

    # print(courses_taken)

    # Filter the course dictionary to remove CS courses the student does not have prerequisites for
    course_dict = parser.filter_course_list_by_prereqs_fulfilled(course_dict, courses_taken)
    course_dict = parser.remove_already_taken_courses(course_dict, courses_taken)


    # for course in course_dict:
    #     print(course_dict[course])

    # Define training parameters for the agent
    # epsilon = 1.0
    # min_epsilon = .05
    # epsilon_decay = .997
    # gamma = .5
    # alpha = .5

    # Train agent and find the best schedule(s)
    agent = Agent(course_dict, episodes, request, epsilon, epsilon_decay, min_epsilon, gamma, alpha)
    agent.init_qtable()
    reward_array = agent.train()
    eval_reward_array = agent.find_best_schedule(request['NumberOfSchedules'])
    print("Average Reward Over Training: ")
    print(sum(reward_array) / len(reward_array))
    print("Average Reward of Final Schedules: ")
    print(sum(eval_reward_array) / len(eval_reward_array))


test()