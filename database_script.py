import requests
from datetime import datetime, timedelta
from rich import print
import json
from twilio.rest import Client
import pytz
account_sid = 'AC073f10733ecc95f504560b1d889f207d'
auth_token = 'dc27373a1c4f16ac740dfb85cf6b5e8f'
client = Client(account_sid, auth_token)

sun_emoji = '\u2600'
# Define the Student class
class Student:
    def __init__(self, id, name, canvas_url, canvas_api_token, personal_phone_number):
        self.id = id
        self.name = name
        self.canvas_url = canvas_url
        self.canvas_api_token = canvas_api_token
        self.personal_phone_number = personal_phone_number
        self.course_names = []
        self.course_ids = []
        self.final_text = []
        self.assignments = []
        self.assignment_counter = 0
    '''
    def get_courses(self):
        headers = {'Authorization': f'Bearer {self.canvas_api_token}'}
        url = f'{self.canvas_url}/api/v1/courses'
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                try:
                    courses = response.json()
                    for course in courses:
                        if 'name' in course:
                            course_id = course['id']
                            course_name = course['name']
                            self.course_ids.append(course_id)
                            self.course_names.append(course_name)
                except ValueError:
                    print("Response content is not valid JSON. The content received:\n", response.text)
                    return
            else:
                print(f"Failed to retrieve courses. Status code: {response.status_code}")
                print("Response content received:\n", response.text)
                return
        except Exception as e:
            print(f"An error occurred getting courses")  '''
    def get_courses(self):
        headers = {'Authorization': f'Bearer {self.canvas_api_token}'}
        url = f'{self.canvas_url}/api/v1/courses'

        try:
            page = 1
            while True:
                params = {
                    'page': page,
                    'per_page': 50,  # You can adjust per_page based on your needs
                }

                response = requests.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    try:
                        courses = response.json()
                        for course in courses:
                            if 'name' in course:
                                course_id = course['id']
                                course_name = course['name']
                                self.course_ids.append(course_id)
                                self.course_names.append(course_name)
                    except ValueError:
                        print("Response content is not valid JSON. The content received:\n", response.text)
                        return
                else:
                    print(f"Failed to retrieve courses. Status code: {response.status_code}")
                    print("Response content received:\n", response.text)
                    return

                # Check if there are more pages
                if 'Link' in response.headers and 'rel="next"' not in response.headers['Link']:
                    break
                else:
                    page += 1

        except Exception as e:
            print(f"An error occurred getting courses: {e}")



   

    def get_todays_assignments_for_course(self, course_ids):
        # Set the date for which you want to get assignments from 1 AM to midnight
        target_date_utc = datetime.utcnow() + timedelta(days=2)

        # Define the Pacific Time zone
        pacific_timezone = pytz.timezone('America/Los_Angeles')

        # Convert UTC time to Pacific Time
        target_date_pacific = target_date_utc.replace(tzinfo=pytz.utc).astimezone(pacific_timezone)

        target_1am_pacific = pacific_timezone.localize(datetime(target_date_utc.year, target_date_utc.month, target_date_utc.day, 1, 0, 0))
        target_midnight_pacific = pacific_timezone.localize(datetime(target_date_utc.year, target_date_utc.month, target_date_utc.day, 23, 59, 59, 999999))


        print("Target date:", target_date_pacific)
        print("Target 1 am time:", target_1am_pacific)
        print("Target midnight time:", target_midnight_pacific)

        for course_id in course_ids:
            headers = {'Authorization': f'Bearer {self.canvas_api_token}'}
            url = f"{self.canvas_url}/api/v1/courses/{course_id}/assignments"

            params = {
                "bucket": "upcoming",  # Filter for upcoming assignments
                "per_page": 20  # Set the number of assignments to retrieve
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                try:
                    assignments = response.json()

                    for assignment in assignments:
                        due_date_str = assignment.get('due_at')
                        if due_date_str:
                            due_date_utc = pytz.utc.localize(datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ"))

                            # Convert assignment due date to Pacific Time
                            due_date_pacific = due_date_utc.replace(tzinfo=pytz.utc).astimezone(pacific_timezone)

                            # Check if the assignment due date is between 1 AM and midnight Pacific Time
                            if target_1am_pacific <= due_date_pacific <= target_midnight_pacific:
                                assignment_info = f" {assignment['name']}"
                                self.assignments.append(assignment_info)
                                self.assignment_counter += 1

                except ValueError:
                    print("Response is not valid JSON.")
            else:
                print(f"Failed to retrieve assignments for Course ID {course_id}. Status code: {response.status_code}")
                print(response.text)


# In-memory student data storage
STUDENTS_DATA = {
    6: {
        'id': 6,
        'name': 'John Doe',
        'canvas_url': 'https://canvas.example.edu',
        'canvas_api_token': 'your_canvas_api_token_here',
        'personal_phone_number': '+1234567890'
    },
    7: {
        'id': 7,
        'name': 'Jane Smith',
        'canvas_url': 'https://canvas.example.edu',
        'canvas_api_token': 'your_canvas_api_token_here',
        'personal_phone_number': '+1234567891'
    }
}

# Function to add a student to in-memory storage
def add_student_to_memory(student_id, name, canvas_url, canvas_api_token, personal_phone_number):
    STUDENTS_DATA[student_id] = {
        'id': student_id,
        'name': name,
        'canvas_url': canvas_url,
        'canvas_api_token': canvas_api_token,
        'personal_phone_number': personal_phone_number
    }
    print(f"Added student {name} (ID: {student_id}) to memory")

# Function to retrieve student data from in-memory storage and create a Student object
def get_student_from_memory(student_id):
    student_data = STUDENTS_DATA.get(student_id)
    if student_data:
        # Create a Student instance with attributes from the in-memory data
        student = Student(
            student_data['id'],
            student_data['name'],
            student_data['canvas_url'],
            student_data['canvas_api_token'],
            student_data['personal_phone_number']
        )
        return student
    else:
        print(f"Student with ID {student_id} not found in memory")
        return None

# Function to list all students in memory
def list_all_students():
    print("Students in memory:")
    for student_id, data in STUDENTS_DATA.items():
        print(f"  ID: {student_id}, Name: {data['name']}")
    return list(STUDENTS_DATA.keys())




if __name__ == "__main__":
    print(f'Retrieving student data from memory...')
    
    for student_id_to_retrieve in range(6, 8):
        try: 
            # Retrieve the student information from in-memory storage
            student = get_student_from_memory(student_id_to_retrieve)
            if student:
                # Print student information
                print(f'Student ID: {student.id}')
                print(f'Student Name: {student.name}')
                print(f'Canvas URL: {student.canvas_url}')
                print(f'Canvas API Token: {student.canvas_api_token}')
                print(f'Personal Phone Number: {student.personal_phone_number}')     
                student.get_courses()
                print(f'Course Names: {student.course_names}')
                print(f'Course IDs: {student.course_ids}')
                #Call the function to get assignments for these courses
                student.get_todays_assignments_for_course(student.course_ids)
                assignment_string = ' and '.join(student.assignments)
                text_message = f'Good Morning {student.name}{sun_emoji}. Today you have {student.assignment_counter} assignment(s) due:\n' + assignment_string
                print(text_message)
        except Exception as e:
            print(f"An error occurred for student ID {student_id_to_retrieve}: {e}")    
