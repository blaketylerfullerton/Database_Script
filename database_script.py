import mysql.connector
from mysql.connector import Error
import requests
import json
from datetime import datetime
from rich import print
import time
from twilio.rest import Client

smily_face = "\U0001F604"
textOut = ""
space = " "
new_line = "\n\n"
book_emoji = "\U0001F4DA"
smily_face = "\U0001F604"
thinking_emoji = '\U0001F914'
red_alert_emoji = '\U00002757'

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

    def get_assignments_for_course(self, course_id):
        # Fetch assignments for a specific course using Canvas API
        headers = {'Authorization': f'Bearer {self.canvas_api_token}'}
        ASSIGNMENTS_ENDPOINT = f'{self.canvas_url}/api/v1/courses/{course_id}/assignments'
        response = requests.get(ASSIGNMENTS_ENDPOINT, headers=headers)

        if response.status_code == 200:
            assignments = json.loads(response.text)
            return assignments
        else:
            return []

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

# Example SQL query
sql_query = """
SELECT * FROM athenalite2;
"""

if __name__ == "__main__":
    # Connect to the database
    connection = connect_to_database()

    if connection:

        # Specify the student ID you want to retrieve
        student_id_to_retrieve = 6
        print(f'Retrieving')

        # Retrieve the student information from the database
        student = get_student_from_database(connection, student_id_to_retrieve)

        if student:
            student.course_names = []
            student.course_ids = []
            student.final_text = []

            # Print the student attributes
            print(f'Retrieving data for {student.name} {smily_face}: ')
            print(f"Database ID: {student.id}")
            print(f"Name: {student.name}")
            print(f"Canvas URL: {student.canvas_url}")
            print(f"Canvas API Token: {student.canvas_api_token}")
            print(f"Phone Number: {student.personal_phone_number}")

            # Make a GET request to a Canvas API endpoint
            endpoint_url = f'{student.canvas_url}/api/v1/courses'
            headers = {'Authorization': f'Bearer {student.canvas_api_token}'}

            try:
                response = requests.get(endpoint_url, headers=headers)

                if response.status_code == 200:
                    # Print the response content (JSON data)
                    user_data = response.json()

                    # Check if user_data is a list, and if it is, access the first item in the list
                    if isinstance(user_data, list) and len(user_data) > 0:
                        user_id = user_data[0]['id']
                        print(f'User ID: {user_id}')

                        # Iterate through the list of courses
                        for course in user_data:
                            # Check if the course object has a 'name' key (indicating it's a course with a name)
                            if 'name' in course:
                                class_id = course['id']
                                class_name = course['name']
                                print(f'Class ID: {class_id}, Class Name: {class_name}')
                                student.course_ids.append(class_id)
                                student.course_names.append(class_name)
                                print(f"{student.name}'s Course ID's:")
                                print(student.course_ids)

                                # Fetch assignments for each course
                                for course_id in student.course_ids:
                                    assignments = student.get_assignments_for_course(course_id)

                                    if assignments:
                                        print(f"Assignments for Course ID {course_id} ({class_name}):")

                                        now = datetime.now()

                                        for assignment in assignments:
                                            due_at_str = assignment.get('due_at')
                                            name = assignment.get('name')

                                            if due_at_str:
                                                assignment_due_at = datetime.strptime(due_at_str, '%Y-%m-%dT%H:%M:%SZ')
                                                if assignment_due_at.date() == now.date():  # Check if due today
                                                    myText = f"{book_emoji}{class_name}: {name}' is due Today{red_alert_emoji}"
                                                    textOut = textOut + space + myText + new_line

                else:
                    print(f"Error: Status Code {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

        # Close the database connection
        connection.close()
        

        # Print the final text with assignments due today
        if textOut:
            textOut = f'Good morning {student.name}, Here are your upcoming assignments for today:\n' + textOut
            print(textOut)
            account_sid = 'AC073f10733ecc95f504560b1d889f207d'
            auth_token = 'dc27373a1c4f16ac740dfb85cf6b5e8f'
            client = Client(account_sid, auth_token)
            #################### SENDING MESSAGE ###############################
            message = client.messages.create(
                from_='+18447314592',
                body= textOut,
                to=f'{student.personal_phone_number}'
            )
        else:
            textOut = (f'Good morning {student.name}, You have no assignments due today! {smily_face}')
            account_sid = 'AC073f10733ecc95f504560b1d889f207d'
            auth_token = 'dc27373a1c4f16ac740dfb85cf6b5e8f'
            client = Client(account_sid, auth_token)
            #################### SENDING MESSAGE ###############################
            message = client.messages.create(
            from_='+18447314592',
            body= textOut,
            to=f'{student.personal_phone_number}'
            )

        




