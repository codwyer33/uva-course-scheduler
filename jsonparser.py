import csv
import re

# Starter code for parsing the CSV from https://www.geeksforgeeks.org/working-csv-files-python/
def parse_csv_into_dict(csv_file_path):
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        course_dict = []
        for row in csv_reader:
            course_dict.append(row)
    return course_dict

# Stores labs/discussions associated with a lecture under their parent lecture using key 'RequiredSections'
# Also removes labs/discussions from course_list
def consolidate_lectures_and_discussions(course_list):
    multi_section_courses = {}

    # Find the types of all courses
    for course in course_list:
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

    # We are assuming that for courses that have lecture and something else, both are required
    # Store non-lecture courses in the multi_section_courses dictionary
    for course in course_list:
        if (course['Mnemonic'], course['Number']) in multi_section_courses:
            if course['Type'] != 'Lecture':
                multi_section_courses[(course['Mnemonic'], course['Number'])].append(course)
                course_list.remove(course)

    for course in course_list:
        if (course['Mnemonic'], course['Number']) in multi_section_courses:
            course['RequiredSections'] = multi_section_courses[(course['Mnemonic'], course['Number'])]

    return course_list

# Stores a list of dictionaries under the 'Times' key, with StartTime and EndTime as minutes since 12am
# Example: Mo 2:00pm - 3:15pm becomes [{'Day': 'Mo', 'StartTime': 840, 'EndTime': 915}] for
def parse_times(course_list):
    for course in course_list:
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

def are_times_overlapping(times1, times2):
    for t1 in times1:
        for t2 in times2:
            if t1['Day'] == t2['Day']:
                if t1['StartTime'] > t2['StartTime'] and t1['EndTime'] < t2['EndTime']:
                    return False
                if t2['StartTime'] > t1['StartTime'] and t2['EndTime'] < t1['EndTime']:
                    return False
    return True

# def train(episodes):
    # for _ in episodes:

course_list = parse_csv_into_dict('classes.csv')

# Remove independent studies and courses with no time for now
for course in course_list:
    if course['Type'] == 'IND':
        course_list.remove(course)
    elif course['Days'] == 'TBA':
        course_list.remove(course)

parse_times(course_list)
course_list = consolidate_lectures_and_discussions(course_list)

for course in course_list:
    print(course['Days'], course['Times'])




