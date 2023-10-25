from twilio.rest import Client
from datetime import datetime, timedelta
import requests
import json
import mysql.connector
from mysql.connector import Error
from rich import print


account_sid = 'AC073f10733ecc95f504560b1d889f207d'
auth_token = 'dc27373a1c4f16ac740dfb85cf6b5e8f'
client = Client(account_sid, auth_token)

sun_emoji = '\u2600'

class Student:
    def __init__(self, id, name, canvas_url, canvas_api_token, personal_phone_number):
        self.id = id
        self.name = name
        self.canvas_url = canvas_url
        self.canvas_api_token = canvas_api_token
        self.personal_phone_number = personal_phone_number
        self.course_names = []
        self.course_ids = []
        self.assignments = []
        self.assignment_counter = 0

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
                    print("Response content is not valid JSON.")
            else:
                print(f"Failed to retrieve courses. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred getting courses")

    def get_hour_from_now_assignments_for_course(self, course_ids):
        for course_id in course_ids:
            headers = {'Authorization': f'Bearer {self.canvas_api_token}'}
            url = f"{self.canvas_url}/api/v1/courses/{course_id}/assignments"
            params = {
                "bucket": "upcoming",
                "per_page": 10
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                try:
                    assignments = response.json()
                    now = datetime.now()
                    for assignment in assignments:
                        due_date_str = assignment.get('due_at')
                        if due_date_str:
                            due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ")
                            # Add one day to the due_date
                            #due_date += timedelta(days=1)
                            time_difference = (due_date - now).total_seconds()
                            if time_difference > 0 and time_difference <= 90000:
                                assignment_info = f" {assignment['name']}"
                                self.assignments.append(assignment_info)
                                self.assignment_counter = self.assignment_counter + 1
                except ValueError:
                    print("Response is not valid JSON.")
            else:
                print(f"Failed to retrieve assignments for Course ID {course_id}. Status code: {response.status_code}")

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            username="doadmin",
            password="AVNS_iuOLTr_1rACvDK-o1Nl",
            host="athena-database-do-user-14760374-0.b.db.ondigitalocean.com",
            port=25060,
            database="defaultdb",
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def get_student_from_database(connection, student_id):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM athenalite2 WHERE id = {student_id}")
        row = cursor.fetchone()
        if row:
            student = Student(row[0], row[1], row[2], row[3], row[4])
            return student
    except Error as e:
        print(f"Error: {e}")
        return None
    


if __name__ == "__main__":
    connection = connect_to_database()
    if connection:
        print(f'Retrieving')
        for student_id_to_retrieve in range(1, 9):
            try:
                student = get_student_from_database(connection, student_id_to_retrieve)
                if student:
                    print(f'Student ID: {student.id}')
                    print(f'Student Name: {student.name}')
                    print(f'Canvas URL: {student.canvas_url}')
                    print(f'Canvas API Token: {student.canvas_api_token}')
                    print(f'Personal Phone Number: {student.personal_phone_number}')
                    student.get_courses()
                    print(f'Course Names: {student.course_names}')
                    print(f'Course IDs: {student.course_ids}')
                    student.get_hour_from_now_assignments_for_course(student.course_ids)
                    assignment_string = ' and '.join(student.assignments)
                    text_message = f'Hey {student.name}!Just a reminder You have {student.assignment_counter} assignment(s) Due in an hour!:\n' + assignment_string 

                    if student.assignment_counter > 0:
                        print(text_message)
                        #message = client.messages.create(
                        #    from_='+18447314592',
                        #    body=text_message,
                         #   to=f'{student.personal_phone_number}'
                        #)
            except Exception as e:
                print(f"An error occurred for student ID {student_id_to_retrieve}: {e}")