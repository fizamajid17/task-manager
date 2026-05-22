from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Task
from app.forms import RegisterForm, LoginForm, TaskForm
from datetime import datetime

auth = Blueprint('auth', __name__)
tasks = Blueprint('tasks', __name__)
main = Blueprint('main', __name__)


# ---------- MAIN ----------

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.board'))
    return redirect(url_for('auth.login'))


# ---------- AUTH ----------

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.board'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.board'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('tasks.board'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# ---------- TASKS ----------

@tasks.route('/board')
@login_required
def board():
    todo = Task.query.filter_by(user_id=current_user.id, status='todo').all()
    inprogress = Task.query.filter_by(user_id=current_user.id, status='inprogress').all()
    done = Task.query.filter_by(user_id=current_user.id, status='done').all()
    total = Task.query.filter_by(user_id=current_user.id).count()
    overdue = Task.query.filter(
        Task.user_id == current_user.id,
        Task.due_date < datetime.utcnow(),
        Task.status != 'done'
    ).count()
    return render_template('tasks/tasks.html',
                           todo=todo, inprogress=inprogress, done=done,
                           total=total, overdue=overdue)


@tasks.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            due_date=datetime.combine(form.due_date.data, datetime.min.time()) if form.due_date.data else None,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added!', 'success')
        return redirect(url_for('tasks.board'))
    return render_template('tasks/add_task.html', form=form, title='New Task')


@tasks.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Not allowed.', 'danger')
        return redirect(url_for('tasks.board'))
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.priority = form.priority.data
        task.due_date = datetime.combine(form.due_date.data, datetime.min.time()) if form.due_date.data else None
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('tasks.board'))
    return render_template('tasks/add_task.html', form=form, title='Edit Task')


@tasks.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Not allowed.', 'danger')
        return redirect(url_for('tasks.board'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'success')
    return redirect(url_for('tasks.board'))


@tasks.route('/task/status/<int:task_id>/<string:new_status>', methods=['POST'])
@login_required
def update_status(task_id, new_status):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.status = new_status
        db.session.commit()
    return redirect(url_for('tasks.board'))