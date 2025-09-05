import streamlit as st
from utils import (
    authenticate, load_users, load_employees, load_tasks,
    assign_task, get_tasks_for_employee, update_task_status,
    log_time_spent, update_task_reason
)
from datetime import date
from performance import show_performance  # Import the performance page function

st.set_page_config(page_title="Employee Performance Platform", layout="centered")
st.title("💼 Employee Performance Management Platform")

# Initialize session state for login and page navigation
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if 'page' not in st.session_state:
    st.session_state.page = 'main'  # default page

# ---- Login screen ----
if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome {user['username']}! Role: {user['role']}")
            st.rerun()
        else:
            st.error("Invalid username or password")

else:
    # ---- Logged-in view ----
    user = st.session_state.user
    st.sidebar.success(f"Logged in as {user['username']} ({user['role']})")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = 'main'  # reset to main page on logout
        st.rerun()

    # Sidebar button for manager to view performance evaluation
    if user["role"] == "Manager":
        if st.sidebar.button("Performance Evaluation"):
            st.session_state.page = 'performance'

    # If on performance page, show Back button
    if st.session_state.page == 'performance':
        if st.sidebar.button("Back to Main"):
            st.session_state.page = 'main'

    # Render pages based on current state
    if st.session_state.page == 'performance':
        show_performance()

    else:
        # ---- MANAGER DASHBOARD ----
        if user["role"] == "Manager":
            st.header("📋 Manager Dashboard")

            st.subheader("Assign a New Task")
            employees = load_employees()
            employee_names = [f"{e['id']}: {e['Employee Name']}" for e in employees]
            selected = st.selectbox("Select Employee", employee_names)
            employee_id = selected.split(":")[0]

            title = st.text_input("Task Title")
            description = st.text_area("Task Description")
            deadline = st.date_input("Deadline", min_value=date.today())
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])

            if st.button("Assign Task"):
                assign_task(employee_id, title, description, str(deadline), priority)
                st.success("✅ Task assigned successfully!")

            import pandas as pd

            st.subheader("📌 All Tasks")
            tasks = load_tasks()

            # Prepare data for display
            task_data = []
            for task in tasks:
                emp_name = next((e['Employee Name'] for e in employees if e['id'] == task['employee_id']), "Unknown")
                task_data.append({
                    "Task ID": task['id'],
                    "Employee": task['employee_id'],
                    "Title": task['title'],
                    "Priority": task.get('priority', 'Not set'),
                    "Status": task['status'],
                    "Deadline": task['deadline'],
                    "Time Spent (hrs)": task['time_spent'],
                    "Reason": task.get('reason', '')
                })

            # Create DataFrame
            df = pd.DataFrame(task_data)

            # Display table
            st.dataframe(df, use_container_width=True)

        # ---- EMPLOYEE DASHBOARD ----
        elif user["role"] == "Employee":
            st.header("👷 Employee Dashboard")

            employee_id = user["employee_id"]
            tasks = get_tasks_for_employee(employee_id)

            if not tasks:
                st.info("You have no tasks assigned.")
            else:
                for task in tasks:
                    st.markdown(f"""
                    **Task ID:** {task['id']}  
                    **Title:** {task['title']}  
                    **Description:** {task['description']}  
                    **Priority:** {task.get('priority', 'Not set')}  
                    **Status:** {task['status']}  
                    **Deadline:** {task['deadline']}  
                    **Time Spent:** {task['time_spent']} hrs
                    """)

                    new_status = st.selectbox(f"Update status for Task {task['id']}",
                                              ["No change", "Assigned", "In Progress", "Done"],
                                              key=f"status_{task['id']}")

                    hours_spent = st.number_input(f"Add hours spent on Task {task['id']}",
                                                  min_value=0.0, step=0.5,
                                                  key=f"hours_{task['id']}")

                    reason = ""
                    if task["status"] != "Done":
                        reason = st.text_area(f"Reason for incomplete Task {task['id']}",
                                              value=task.get("reason", ""),
                                              key=f"reason_{task['id']}")

                    if st.button(f"Update Task {task['id']}", key=f"update_{task['id']}"):
                        if new_status != "No change":
                            update_task_status(task['id'], new_status)
                        if hours_spent > 0:
                            log_time_spent(task['id'], hours_spent)
                        if reason.strip():
                            update_task_reason(task['id'], reason.strip())
                        st.success(f"Task {task['id']} updated successfully!")
                        st.rerun()
