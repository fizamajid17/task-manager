# TaskBoard — Task Management Web App

A full stack task management web app built with Python and Flask.

## Features
- User registration and login with session management
- Kanban board with three columns — To Do, In Progress, Done
- Create, edit, and delete tasks
- Priority levels (low, medium, high) and due dates
- Dashboard stats showing total, completed, in progress, and overdue tasks

## Tech Stack
- **Backend:** Python, Flask, Flask-Login, Flask-WTF
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** Jinja2 templates, Bootstrap 5

## Run locally

```bash
git clone https://github.com/fizamajid17/task-manager.git
cd task-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000 in your browser.