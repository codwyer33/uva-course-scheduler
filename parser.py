import copy
import csv
import re

class Parser:
    # def __init__(self):
    #     # self.course_list = course_list

    # Starter code for parsing the CSV from https://www.geeksforgeeks.org/working-csv-files-python/
    def parse_csv_into_dict(self, csv_file_path):
        with open(csv_file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            course_dict = {}
            for row in csv_reader:
                this_course_dict = row
                course_dict[this_course_dict['ClassNumber']] = row
        return course_dict

    # Stores labs/discussions associated with a lecture under their parent lecture using key 'RequiredSections'
    # Also removes labs/discussions from course_list
    def consolidate_lectures_and_discussions(self, course_list):
        multi_section_courses = {}

        # Find the types of all courses
        for key in course_list:
            course = course_list[key]
            if (course['Mnemonic'], course['Number']) not in multi_section_courses: # initialize this course code entry
                multi_section_courses[(course['Mnemonic'], course['Number'])] = [course['Type']]
            elif course['Type'] not in multi_section_courses[(course['Mnemonic'], course['Number'])]:
                # add to this course code entry if the type does not match
                multi_section_courses[(course['Mnemonic'], course['Number'])].append(course['Type']);

        # Identify only courses that include both lecture and discussion/lab
        for key in list(multi_section_courses):
            this_course_list = multi_section_courses[key]
            if not ('Lecture' in this_course_list and len(this_course_list) > 1):
                del multi_section_courses[key]
            else:
                multi_section_courses[key] = []

        # print("M", multi_section_courses)

        # We are assuming that for courses that have lecture and something else, both are required
        # Store non-lecture courses in the multi_section_courses dictionary
        for key in course_list:
            course = course_list[key]
            if (course['Mnemonic'], course['Number']) in multi_section_courses:
                if course['Type'] != 'Lecture':
                    multi_section_courses[(course['Mnemonic'], course['Number'])].append(key)
                    # print("update m", multi_section_courses)

        for key in course_list:
            course = course_list[key]
            if (course['Mnemonic'], course['Number']) in multi_section_courses and course['Type'] == 'Lecture':
                course['RequiredSections'] = multi_section_courses[(course['Mnemonic'], course['Number'])]
                # print()
                # print("making required sections", course_list[key])

        return course_list

    # Stores a list of dictionaries under the 'Times' key, with StartTime and EndTime as minutes since 12am
    # Example: Mo 2:00pm - 3:15pm becomes [{'Day': 'Mo', 'StartTime': 840, 'EndTime': 915}] for
    def parse_times(self, course_list):
        for key in course_list:
            course = course_list[key]
            parts = course['Days'].split(' ')
            if len(parts) < 4:
                return

            days = parts[0]
            start_time = parts[1].split(':')
            end_time = parts[3].split(':')

            # Convert to 24-hour format
            start_time_hr = start_time[0]
            start_time_min = start_time[1][0:-2]
            start_time_ampm = start_time[1][-2]
            end_time_hr = end_time[0]
            end_time_min = end_time[1][0:-2]
            end_time_ampm = end_time[1][-2]

            start_time_total_min = 60*int(start_time_hr) + int(start_time_min)
            end_time_total_min = 60*int(end_time_hr) + int(end_time_min)

            if start_time_ampm == 'p' and int(start_time_hr) != 12:
                start_time_total_min += 12*60
            if end_time_ampm == 'p' and int(end_time_hr) != 12:
                end_time_total_min += 12*60

            # Split days and create entries
            course['Times'] = []
            for day in re.findall(r"Mo|Tu|We|Th|Fr|Sa|Su", days):
                course['Times'].append({'Day': day, 'StartTime': start_time_total_min, 'EndTime': end_time_total_min})

        # return course_list

    # Filter out courses that have incomplete data or are not typical undergraduate courses
    def remove_extra_courses(self, course_list):
        # Remove independent studies and courses with no time for now
        new_list = copy.deepcopy(course_list)
        for course in course_list:
            if course_list[course]['Type'] == "IND":
                del new_list[course]
            elif course_list[course]['Days'] == "TBA":
                del new_list[course]
            elif "no mtgs" in course_list[course]['Days']:
                del new_list[course]
            elif int(course_list[course]['Number']) >= 6000:
                del new_list[course]
            elif int(course_list[course]['Mnemonic'] == "EGMT"):
                del new_list[course]
            elif int(course_list[course]['Mnemonic'] =="ESL"):
                del new_list[course]
        return new_list


    # Add prereqs for CS courses through manually assembled list
    def add_prereqs(self, course_list):

        prereq_list = {('CS', '2100'): [['CS 1100'], ['CS 1111'], ['CS 1112'], ['CS 1113']],
                       ('CS', '2120'): [['CS 1100'], ['CS 1111'], ['CS 1112'], ['CS 1113']],
                       ('CS', '2130'): [['CS 1100'], ['CS 1111'], ['CS 1112'], ['CS 1113']],
                       ('CS', '3100'): [['CS 2100', 'CS 2120', 'APMA 1090'],
                                        ['CS 2100', 'CS 2120', 'APMA 1310'],
                                        ['CS 2100', 'CS 2120', 'APMA 1210'],
                                        ['CS 2100', 'CS 2120', 'APMA 1110']],
                       ('CS', '3120'): [['CS 3100']],
                       ('CS', '3130'): [['CS 2100', 'CS 2130']],
                       ('CS', '3140'): [['CS 2100']],
                       ('CS', '3205'): [['CS 2110'], ['CS 2100']],
                       ('CS', '3240'): [['CS 2150'], ['CS 3140']],
                       ('CS', '3250'): [['CS 2150'], ['CS 2100', 'CS 2120']],
                       ('CS', '3710'): [['CS 2150'], ['CS 2100']],
                       ('CS', '4260'): [['CS 3240']],
                       ('CS', '4444'): [['CS 3100', 'CS 3130']],
                       ('CS', '4457'): [['CS 3330'],
                                        ['CS 2501'],
                                        ['ECE 3420'],
                                        ['ECE 4435'],
                                        ['ECE 3502'],
                                        ['CS 3130']],
                       ('CS', '4610'): [['CS 2150'], ['CS 2120', 'CS 3140']],
                       ('CS', '4630'): [['CS 3710']],
                       ('CS', '4710'): [['CS 2150'], ['CS 3140']],
                       ('CS', '4720'): [['CS 2150'], ['CS 3140']],
                       ('CS', '4740'): [['CS 2150'], ['CS 3140']],
                       ('CS', '4750'): [['CS 2150'], ['CS 2120', 'CS 3140']],
                       ('CS', '4774'): [['CS 3100', 'APMA 3100', 'MATH 3350'],
                                        ['CS 3100', 'APMA 3100', 'APMA 3080'],
                                        ['CS 3100', 'APMA 3110', 'MATH 3350'],
                                        ['CS 3100', 'APMA 3110', 'APMA 3080'],
                                        ['CS 3100', 'MATH 3100', 'MATH 3350'],
                                        ['CS 3100', 'MATH 3100', 'APMA 3080']],
                       ('CS', '4971'): [['CS 4970']],
                       ('CS', '4980'): [['CS 3140']],
                       ('CS', '4998'): [['CS 2150'], ['CS 2501']],
                       ('CS', '6111'): [['CS 4457']]}

        for key in prereq_list:
            for course_key in course_list:
                if course_list[course_key]['Mnemonic'] == key[0] and course_list[course_key]['Number'] == key[1]:
                    course_list[course_key]['Prerequisites'] = prereq_list[key]

        return course_list

    def passed_course(self, course, courses_taken): #Returns true if student get C- or better
        if course not in courses_taken:
            return False
        grade = courses_taken[course]
        accepted = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-']
        return grade in accepted

    # Remove courses a student doesn't have the prereqs for
    def filter_course_list_by_prereqs_fulfilled(self, courses_dict, courses_taken):
        filtered_courses = {}

        for course_key, course_info in courses_dict.items():
            if 'Prerequisites' not in course_info:
                filtered_courses[course_key] = course_info
                continue

            prereq_options = course_info['Prerequisites']

            # Check if any prereq option is fully satisfied
            fulfills_any_option = any(
                all(self.passed_course(prereq, courses_taken) for prereq in option)
                for option in prereq_options
            )

            if fulfills_any_option:
                filtered_courses[course_key] = course_info
            # if not fulfills_any_option:
            #     print(course_info)
        return filtered_courses

    def remove_already_taken_courses(self, course_dict, courses_taken):
        filtered_courses = {
            key: value for key, value in course_dict.items()
            if not self.passed_course(f"{value['Mnemonic']} {value['Number']}", courses_taken)
        }
        return filtered_courses

