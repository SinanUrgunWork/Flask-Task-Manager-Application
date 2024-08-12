from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from datetime import datetime

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # Unique identifier for each user
    username = db.Column(db.String(80), unique=True, nullable=False) # Username must be unique and non-null
    _password = db.Column("password", db.String(120), nullable=False) # Password is stored as a hashed value
    tasks = db.relationship('Task', back_populates='owner', lazy='dynamic', cascade="all, delete-orphan") # One-to-many relationship with tasks
    is_admin = db.Column(db.Boolean, default=False) # Indicates if the user has admin privileges

    def is_administrator(self):
        return self.is_admin
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute') # Prevents direct reading of password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)  # Hashes the password before storing it

    def verify_password(self, password):
        return check_password_hash(self._password, password) # Verifies a password against the stored hash

# Task Model
class TaskStatus(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.NOT_STARTED, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign key linking task to user
    owner = db.relationship('User', back_populates='tasks') # Relationship back to the user who owns the task
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # Timestamp when the task was created
    permissions = db.relationship('Permission', back_populates='task', cascade="all, delete-orphan") # Relationship to permissions with cascading deletes
    

# Permission Model
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign key linking permission to user
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False) # Foreign key linking permission to task
    task = db.relationship('Task', back_populates='permissions') # Relationship back to the task
    user = db.relationship('User') # Relationship back to the user
    can_view = db.Column(db.Boolean, default=False)
    can_view_status = db.Column(db.Boolean, default=True)
'''

+------------------+         +------------------+        +------------------+
|     User         |         |      Task        |        |    Permission    |
+------------------+         +------------------+        +------------------+
| id (PK)          | 1    n  | id (PK)          | 1   n  | id (PK)          |
| username         +-------->| user_id (FK)     +------->| task_id (FK)     |
| password         |         | title            |        | user_id (FK)     |
| is_admin         |         | description      |        | can_view         |
+------------------+         | status           |        | can_view_status  |
                             | timestamp        |        +------------------+
                                ...
                             +------------------+

Legend:
- "1 n" indicates a one-to-many relationship.
- "FK" denotes a foreign key.
- "PK" denotes a primary key.

Explanation:
- A **User** can have many **Tasks** (1-to-many relationship).
- A **Task** can be associated with many **Permissions** (1-to-many relationship).
- A **Permission** ties together **Users** and **Tasks**, indicating which users can view or modify which tasks.


'''