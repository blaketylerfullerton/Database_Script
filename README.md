# Canvas Assignment Reminder

This Python script connects to a MySQL database to retrieve student information and sends reminders about upcoming Canvas assignments via SMS using the Twilio API.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3
- Required Python packages (install using `pip install -r requirements.txt`):
  - requests
  - rich
  - mysql-connector-python
  - twilio

## Configuration

1. Install dependencies: `pip install -r requirements.txt`
2. Set up a Twilio account and obtain your `account_sid` and `auth_token`.
3. Update the `account_sid` and `auth_token` variables in the script with your Twilio credentials.
4. Set up a MySQL database and update the database connection details in the `connect_to_database` function.

## Usage

Run the script using the following command:

```bash
python script_name.py
