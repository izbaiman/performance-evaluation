import json
from datetime import datetime
from werkzeug.security import check_password_hash

EMPLOYEE_FILE = "data/employees.json"
TASK_FILE = "data/tasks.json"
USER_FILE = "data/users.json"

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def load_employees():
    with open(EMPLOYEE_FILE, "r") as f:
        return json.load(f)

def load_tasks():
    with open(TASK_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def get_tasks_for_employee(employee_id):
    tasks = load_tasks()
    return [task for task in tasks if str(task['employee_id']) == str(employee_id)]

def update_task_status(task_id, new_status):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            break
    save_tasks(tasks)

def log_time_spent(task_id, hours):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['time_spent'] += hours
            break
    save_tasks(tasks)

def update_task_reason(task_id, reason):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['reason'] = reason
            break
    save_tasks(tasks)

def assign_task(employee_id, title, description, deadline, priority):
    tasks = load_tasks()
    new_task = {
        "id": len(tasks) + 1,
        "employee_id": employee_id,
        "title": title,
        "description": description,
        "status": "Assigned",
        "assigned_on": datetime.now().strftime("%Y-%m-%d"),
        "deadline": deadline,
        "priority": priority,
        "time_spent": 0,
        "reason": ""
    }
    tasks.append(new_task)
    save_tasks(tasks)
