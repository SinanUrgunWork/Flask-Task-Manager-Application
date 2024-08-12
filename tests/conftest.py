import pytest
from app import create_app, db
from app.models import User, Task

@pytest.fixture(scope='function')
def app():
    app = create_app('config.TestConfig')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        user = User(username='testuser', password='testpassword')
        admin = User(username='admin', password='adminpassword', is_admin=True)
        task = Task(title='Test Task', description='This is a test task', user_id=1)
        db.session.add_all([user, admin, task])
        db.session.commit()
        yield user, admin, task

@pytest.fixture(scope='function')
def logged_in_user(client, init_database):
    user, _, _ = init_database
    client.post('/login', data={'username': 'testuser', 'password': 'testpassword'})
    return user

@pytest.fixture(scope='function')
def logged_in_admin(client, init_database):
    _, admin, _ = init_database
    client.post('/login', data={'username': 'admin', 'password': 'adminpassword'})
    return admin