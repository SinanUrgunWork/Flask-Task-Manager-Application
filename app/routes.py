from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Task, Permission, TaskStatus
from .utils import admin_required
from . import db

# Create a Blueprint named 'main'
main = Blueprint('main', __name__)

# Welcome Page Route
@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.tasks'))
    return render_template('index.html')

# Log in Page Route
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.tasks'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

# Log out Route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Route for user registration
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return render_template('register.html')

        user = User(username=username, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            print(str(e))

    return render_template('register.html')

# Route to display tasks
@main.route('/tasks')
@login_required
def tasks():
    all_tasks = []
    if current_user.is_administrator():
        all_tasks = Task.query.all()
    else:
        owned_tasks = Task.query.filter_by(user_id=current_user.id).all()
        shared_tasks = Task.query.join(Permission).filter(
            Permission.user_id == current_user.id,
            Permission.can_view == True
        ).all()
        all_tasks = owned_tasks + shared_tasks

    return render_template('tasks.html', tasks=all_tasks, TaskStatus=TaskStatus)

# Route for editing/creating a task
@main.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@main.route('/task/new', methods=['GET', 'POST'])
@login_required
def edit_task(task_id=None):
    task = None
    if task_id:
        task = db.session.get(Task, task_id)
        if not task or (task.user_id != current_user.id and not current_user.is_administrator()):
            flash('You do not have permission to edit this task.')
            return redirect(url_for('main.tasks'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        if task:
            task.title = title
            task.description = description
        else:
            new_task = Task(title=title, description=description, user_id=current_user.id)
            db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('main.tasks'))

    return render_template('edit_task.html', task=task)

# Share Task Route
@main.route('/task/share/<int:task_id>', methods=['POST'])
@login_required
def share_task(task_id):
    task = db.session.get(Task, task_id)
    if not task or (task.user_id != current_user.id and not current_user.is_administrator()):
        flash('You do not have permission to share this task.', 'danger')
        return redirect(url_for('main.tasks'))

    username = request.form['username']
    user_to_share_with = User.query.filter_by(username=username).first()

    if user_to_share_with:
        existing_permission = Permission.query.filter_by(task_id=task_id, user_id=user_to_share_with.id).first()
        if existing_permission:
            existing_permission.can_view = True
            existing_permission.can_view_status = True
            db.session.commit()
            flash(f'Task has already been shared with {username}. Permissions updated.', 'info')
        else:
            permission = Permission(task_id=task_id, user_id=user_to_share_with.id, can_view=True, can_view_status=True)
            db.session.add(permission)
            db.session.commit()
            flash('Task shared successfully with ' + username, 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('main.tasks'))

# Route for updating the status of a task
@main.route('/task/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = db.session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        flash('You do not have permission to update this task.', 'danger')
        return redirect(url_for('main.tasks'))

    new_status = request.form.get('status')
    if new_status in TaskStatus.__members__:
        task.status = TaskStatus[new_status]
        db.session.commit()
        flash('Task status updated successfully.', 'success')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('main.tasks'))

# Route for deleting a task
@main.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        flash('You do not have permission to delete this task.')
        return redirect(url_for('main.tasks'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.')
    return redirect(url_for('main.tasks'))

# ADMIN: Manage Users and Tasks

# Route to view and manage all users
@main.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

# Route to toggle a user's admin status
@main.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = db.session.get(User, user_id)

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('main.admin_users'))

    if user.username.lower() == "sinan":
        flash('The admin status of "sinan" cannot be changed.', 'danger')
        return redirect(url_for('main.admin_users'))

    if user == current_user:
        flash('You cannot change your own admin status.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status for {user.username} has been {"granted" if user.is_admin else "revoked"}.', 'success')
    return redirect(url_for('main.admin_users'))

# Route to view and manage all tasks
@main.route('/admin/tasks')
@login_required
@admin_required
def admin_tasks():
    tasks = Task.query.all()
    return render_template('admin_tasks.html', tasks=tasks)

# Route to edit a task
@main.route('/admin/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_task(task_id):
    task = db.session.get(Task, task_id)

    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('main.admin_tasks'))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']

        if 'status' in request.form and not current_user.is_administrator():
            task.status = TaskStatus(request.form['status'])
        db.session.commit()

        flash('Task updated successfully.', 'success')
        return redirect(url_for('main.admin_tasks'))

    return render_template('admin_edit_task.html', task=task)

# Route to delete a task
@main.route('/admin/delete_task/<int:task_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('main.admin_tasks'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.', 'success')
    return redirect(url_for('main.admin_tasks'))

# Route to delete a user
@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('main.admin_users'))

    if user.username.lower() == "sinan":
        flash('The user "sinan" cannot be deleted.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" has been deleted successfully.', 'success')

    return redirect(url_for('main.admin_users'))
