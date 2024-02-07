#!/usr/bin/env python
import http.client
import json
import uuid
import os
from urllib.parse import urlparse
from datetime import datetime, timedelta

# start_date = datetime(2024, 2, 1)
# end_date = datetime(2024, 2, 29)

start_date = datetime.now()
end_date = datetime.now()

kronos_domain = "https://kronos.tarento.com"

tasks = {
    'Deployment': 6,
    'Support': 7,
    'Project Management': 9,
    'Meetings': 40
}

def generate_uuid():
    return str(uuid.uuid4())

def get_authorization_token(email, password):
    url = kronos_domain + '/api/v1/user/login'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = {
        "username": email,
        "password" : password
    }

    parsed_url = urlparse(url)
    connection = http.client.HTTPSConnection(parsed_url.netloc)
    path = parsed_url.path

    connection.request('POST', path, body=json.dumps(data), headers=headers)
    response = connection.getresponse()
    response_data = response.read().decode('utf-8')

    # extract authorization token
    authorization_token = json.loads(response_data)['responseData']['sessionId'] 
    return authorization_token

def save_task_time(date, note, authorization_token, task_id, minute=480):
    url = kronos_domain + '/api/v1/user/saveTaskTimeForProject'
    headers = {
        'Authorization': authorization_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    activity_ref_number = os.environ['KRONOS_EMAIL'] + f"#{generate_uuid()}"

    data = {
        "time": [
            {
                "date": date,
                "pid": 2429,
                "tid": task_id,
                "minute": minute,
                "note": note,
                "locId": 8,
                "billable": True,
                "onSite": False,
                "activityRefNumber": activity_ref_number
            }
        ]
    }

    parsed_url = urlparse(url)
    connection = http.client.HTTPSConnection(parsed_url.netloc)
    path = parsed_url.path

    connection.request('POST', path, body=json.dumps(data), headers=headers)
    response = connection.getresponse()
    response_data = response.read().decode('utf-8')

    return response.status, response_data

# check if Kronos credentials are present in env
if 'KRONOS_EMAIL' not in os.environ or 'KRONOS_PASSWORD' not in os.environ:
    raise ValueError("KRONOS_EMAIL or KRONOS_PASSWORD not found in env")
else:
    authorization_token = get_authorization_token(os.environ['KRONOS_EMAIL'], os.environ['KRONOS_PASSWORD'])
    if not authorization_token:
        raise ValueError("authorization_token not found")

current_date = start_date
while current_date <= end_date:
    # Check if the current date is not a Saturday or Sunday
    if current_date.weekday() < 5:  # Monday to Friday
        date_str = current_date.strftime("%Y-%m-%d")

        

        note_input = "NOC Team Support"
        task_id = tasks['Support']
        minute = 480 # Total minutes spent on above task
        status_code, response_json = save_task_time(date_str, note_input, authorization_token, task_id, minute)
        print(f"For {date_str}: Status Code: {status_code}, Response JSON: {response_json}")

        # note_input = "Production Deployment Support"
        # task_id = tasks['Deployment']
        # minute = 360 # Total minutes spent on above task
        # status_code, response_json = save_task_time(date_str, note_input, authorization_token, task_id, minute)
        # print(f"For {date_str}: Status Code: {status_code}, Response JSON: {response_json}")

    current_date += timedelta(days=1)
