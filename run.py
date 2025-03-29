from agent import *
from parser import *

def main():
    episodes = 100

    parser = Parser()
    course_list = parser.parse_csv_into_dict('classes.csv')
    course_list = parser.remove_extra_courses(course_list)
    parser.parse_times(course_list)
    course_list = parser.consolidate_lectures_and_discussions(course_list)

    for course in course_list:
        print(course)

    agent = Agent(course_list, episodes)


main()