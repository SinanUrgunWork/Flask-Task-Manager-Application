import pytest
from app.models import User, Task
from app import db

# Unit Tests

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<title>" in response.data

def test_registration(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

def test_login_logout(client, init_database):
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Logout" in response.data

    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_create_task(logged_in_user, client):
    response = client.post('/task/new', data={
        'title': 'New Task',
        'description': 'This is a new task'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"New Task" in response.data

def test_admin_access(logged_in_admin, client):
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b"Manage Users" in response.data

def test_non_admin_access(logged_in_user, client):
    response = client.get('/admin/users')
    assert response.status_code == 403

def test_share_task(logged_in_user, client, init_database):
    _, _, task = init_database
    response = client.post(f'/task/share/{task.id}', data={
        'username': 'admin'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Task shared successfully" in response.data

def test_update_task_status(logged_in_user, client, init_database):
    _, _, task = init_database
    response = client.post(f'/task/update_status/{task.id}', data={
        'status': 'IN_PROGRESS'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Task status updated successfully" in response.data

def test_delete_task(logged_in_user, client, init_database):
    _, _, task = init_database
    response = client.post(f'/task/delete/{task.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Task deleted successfully" in response.data

def test_admin_users_page(logged_in_admin, client):
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'Manage Users' in response.data
    assert b'Username' in response.data
    assert b'Admin Status' in response.data

def test_toggle_admin_status(logged_in_admin, client, init_database):
    user, _, _ = init_database
    response = client.post(f'/admin/toggle_admin/{user.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Admin status for testuser has been granted' in response.data

    response = client.post(f'/admin/toggle_admin/{user.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Admin status for testuser has been revoked' in response.data

def test_cannot_change_sinan_admin_status(logged_in_admin, client, app):
    with app.app_context():
        sinan = User(username='sinan', password='password')
        db.session.add(sinan)
        db.session.commit()
        
        response = client.post(f'/admin/toggle_admin/{sinan.id}', follow_redirects=True)
        # &#34;sinan&#34; came from print
        print(response.get_data(as_text=True))
        assert response.status_code == 200
        # Adjusted assertion to match HTML encoded content
        assert 'The admin status of &#34;sinan&#34; cannot be changed.' in response.get_data(as_text=True)

def test_admin_tasks_page(logged_in_admin, client):
    response = client.get('/admin/tasks')
    assert response.status_code == 200
    assert b'Manage All Tasks' in response.data
    assert b'Title' in response.data
    assert b'Owner' in response.data
    assert b'Status' in response.data

def test_admin_edit_task(logged_in_admin, client, init_database):
    _, _, task = init_database
    response = client.post(f'/admin/edit_task/{task.id}', data={
        'title': 'Updated Task Title',
        'description': 'Updated task description',
        'status': 'IN_PROGRESS'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Task updated successfully' in response.data
    assert b'Updated Task Title' in response.data

def test_admin_delete_task(logged_in_admin, client, init_database):
    _, _, task = init_database
    response = client.post(f'/admin/delete_task/{task.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Task deleted successfully" in response.data

def test_cannot_delete_sinan_user(logged_in_admin, client, app):
    with app.app_context():
        sinan = User(username='sinan', password='password')
        db.session.add(sinan)
        db.session.commit()
        
        response = client.post(f'/admin/delete_user/{sinan.id}', follow_redirects=True)
        assert response.status_code == 200
        assert 'The user &#34;sinan&#34; cannot be deleted.' in response.get_data(as_text=True)


# Integration Tests

def test_user_registration(client, app):
    with app.app_context():
        # Register a new user
        response = client.post('/register', data={
            'username': 'integrationtestuser',
            'password': 'integrationpassword'
        }, follow_redirects=True)
        
        # Check that the registration was successful
        assert response.status_code == 200
        assert b"Login" in response.data
        
        # Verify that the user exists in the database
        user = User.query.filter_by(username='integrationtestuser').first()
        assert user is not None
        assert user.username == 'integrationtestuser'


def test_task_creation_flow(client, logged_in_user, app):
    with app.app_context():
        # Create a new task
        response = client.post('/task/new', data={
            'title': 'Integration Test Task',
            'description': 'This is a task created during an integration test.'
        }, follow_redirects=True)
        
        # Check that the task creation was successful
        assert response.status_code == 200
        assert b"Integration Test Task" in response.data
        
        # Verify that the task was added to the database
        task = Task.query.filter_by(title='Integration Test Task').first()
        assert task is not None
        assert task.title == 'Integration Test Task'
        assert task.description == 'This is a task created during an integration test.'
        assert task.user_id == logged_in_user.id