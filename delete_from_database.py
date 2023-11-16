import mysql.connector
from mysql.connector import Error

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

def delete_student_from_database(connection, student_id):
    try:
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM athenalite2 WHERE id = {student_id}")
        connection.commit()
        print(f"Deleted student with ID {student_id}")
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    connection = connect_to_database()
    if connection:
        for student_id_to_delete in [9]:  # Replace with the IDs you want to delete
            delete_student_from_database(connection, student_id_to_delete)
        
        connection.close()
