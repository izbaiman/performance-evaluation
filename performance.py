import streamlit as st
import matplotlib.pyplot as plt
from utils import load_tasks, load_employees
from datetime import datetime

st.set_page_config(page_title="📊 Performance Dashboard", layout="wide")
st.title("📊 Employee Performance Analysis")

tasks = load_tasks()
employees = load_employees()


def get_employee_name(emp_id):
    for emp in employees:
        if str(emp["id"]) == str(emp_id):
            return emp["Employee Name"]
    return "Unknown"


# --- Process tasks per employee ---
employee_stats = {}
for task in tasks:
    emp_id = task["employee_id"]
    emp_name = get_employee_name(emp_id)

    if emp_name not in employee_stats:
        employee_stats[emp_name] = {
            "Assigned": 0,
            "In Progress": 0,
            "Done": 0,
            "total": 0,
            "score": 100,
            "high_priority_issues": 0
        }

    status = task["status"]
    priority = task.get("priority", "Medium")
    deadline = task.get("deadline", "")
    is_done = status == "Done"

    # Count task status
    if status in employee_stats[emp_name]:
        employee_stats[emp_name][status] += 1
    else:
        employee_stats[emp_name][status] = 1

    employee_stats[emp_name]["total"] += 1

    # Penalty logic
    if priority == "High" and not is_done:
        employee_stats[emp_name]["score"] -= 10
        employee_stats[emp_name]["high_priority_issues"] += 1
    elif priority == "High" and is_done and deadline:
        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d")
            if datetime.now() > deadline_dt:
                employee_stats[emp_name]["score"] -= 10
                employee_stats[emp_name]["high_priority_issues"] += 1
        except:
            pass

# --- UI Rendering ---
for emp_name, stats in employee_stats.items():
    with st.expander(f"📌 {emp_name} — Score: {stats['score']}"):
        st.write("### Task Completion Breakdown")

        # Pie chart
        labels = ['Assigned', 'In Progress', 'Done']
        sizes = [stats.get('Assigned', 0), stats.get('In Progress', 0), stats.get('Done', 0)]
        colors = ['#FFA726', '#42A5F5', '#66BB6A']

        fig, ax = plt.subplots(figsize=(10, 4))  # Smaller chart
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=40, colors=colors)
        ax.axis('equal')
        st.pyplot(fig)

        # Raw numbers
        st.markdown(f"""
        - **Total Tasks**: {stats['total']}  
        - ✅ **Completed (Done)**: {stats.get('Done', 0)}  
        - 🔄 **In Progress**: {stats.get('In Progress', 0)}  
        - 🕗 **Pending (Assigned)**: {stats.get('Assigned', 0)}  
        - 🚨 **High Priority Issues**: {stats['high_priority_issues']}  
        - 🎯 **Score**: `{stats['score']} / 100`
        """)

# Optionally: Rank employees
st.subheader("🏆 Leaderboard")
sorted_emps = sorted(employee_stats.items(), key=lambda x: x[1]['score'], reverse=True)
for i, (emp_name, stats) in enumerate(sorted_emps, start=1):
    st.markdown(f"**{i}. {emp_name}** — Score: `{stats['score']}`")
