import requests
from datetime import datetime, timedelta
from rich import print
import json
import mysql.connector
from mysql.connector import Error
from twilio.rest import Client
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
    
    def get_courses(self):
        headers = {'Authorization': f'Bearer {self.canvas_api_token}'}
        url = f'{student.canvas_url}/api/v1/courses'
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
            print(f"An error occurred getting courses")  


    def get_todays_assignments_for_course(self, course_ids):
        for course_id in course_ids:
            headers = {'Authorization': f'Bearer {self.canvas_api_token}'}
            url = f"{self.canvas_url}/api/v1/courses/{course_id}/assignments"
            
            params = {
                "bucket": "upcoming",  # Filter for upcoming assignments
                "per_page": 10  # Set the number of assignments to retrieve
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                try:
                    assignments = response.json()
                    
                    tomorrow = datetime.now() #+ timedelta(days=1)
                    
                    for assignment in assignments:
                        due_date_str = assignment.get('due_at')
                        if due_date_str:
                            due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M:%SZ")
                            if due_date.date() == tomorrow.date():
                                assignment_info = f" {assignment['name']}"
                                self.assignments.append(assignment_info)
                                self.assignment_counter = self.assignment_counter + 1
                                
                except ValueError:
                    print("Response is not valid JSON.")
            else:
                print(f"Failed to retrieve assignments for Course ID {course_id}. Status code: {response.status_code}")
                print(response.text)

# Function to connect to the MySQL database
def connect_to_database():
    try:
        # Establish a connection to the MySQL server
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


# Function to retrieve a row from the database and create a Student object
def get_student_from_database(connection, student_id):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM athenalite2 WHERE id = {student_id}")
        row = cursor.fetchone()

        if row:
            # Create a Student instance with attributes from the row
            student = Student(row[0], row[1], row[2], row[3], row[4])
            return student
    except Error as e:
        print(f"Error: {e}")
        return None




if __name__ == "__main__":
    # Connect to the database
    connection = connect_to_database()

    if connection:
        print(f'Retrieving')
        for student_id_to_retrieve in range(1, 9):
            try: 
                # Retrieve the student information from the database
                student = get_student_from_database(connection, student_id_to_retrieve)
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
                    #message = client.messages.create(
                    #from_='+18447314592',
                    #body= text_message,
                    #to=f'{student.personal_phone_number}'
                    #)
            except Exception as e:
                print(f"An error occurred for student ID {student_id_to_retrieve}: {e}")    

            

        
