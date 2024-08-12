# Flask Task Manager Application

This is a simple Task Manager web application built with Flask, SQLite, and Docker. It allows users to manage tasks with features like task creation, task editing, task sharing, and user management. The application also includes an admin interface for managing users and tasks.

## Features

- **User Registration and Authentication**: Users can register, log in, and log out.
- **Task Management**: Users can create, edit, delete, and view tasks. Tasks can be shared with other users.
- **Admin Interface**: Admin users can manage all users and tasks within the application.
- **Role-Based Access Control**: Only admin users can manage other users and tasks.
- **Responsive UI**: The application uses Bootstrap for a responsive and modern user interface.

## Project Structure

```plaintext
.
├── app/
│   ├── __init__.py             # Application factory and initialization
│   ├── models.py               # Database models
│   ├── routes.py               # Application routes and views
│   ├── utils.py                # Utility functions and decorators
│   ├── static/                 # Static files (CSS, JavaScript, images)
│   │   └── style.css           # Custom styles for the application
│   └── templates/              # HTML templates
│       ├── base.html           # Base template
│       ├── index.html          # Home page template
│       ├── login.html          # Login page template
│       ├── register.html       # Registration page template
│       ├── tasks.html          # Task list template
│       ├── edit_task.html      # Task edit/create template
│       ├── admin_users.html    # Admin user management template
│       ├── admin_tasks.html    # Admin task management template
│       └── admin_edit_task.html # Admin task edit template
├── instance/                   # Instance folder for SQLite database
├── migrations/                 # Database migrations (Flask-Migrate)
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures
│   └── test_routes.py          # Test cases for the routes
├── venv/                       # Python virtual environment
├── .env                        # Environment variables
├── .gitignore                  # Git ignore file
├── Dockerfile                  # Docker configuration for the application
├── docker-compose.yml          # Docker Compose configuration
├── app.py                      # Application entry point
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation

```
### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name

2. **Create a virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txte
3. **Set up the environment variables:**  
Create a .env file in the root directory with the following content:
   ```bash
   SECRET_KEY=your_secret_key
   SQLALCHEMY_DATABASE_URI=sqlite:///myflaskapp.db
   FLASK_APP=app
4. **Run the application:**
   ```bash
   flask run
5. **Access the application:**  
   Navigate to http://127.0.0.1:5000 in your web browser.

## Running with Docker  
1. **Build and run the application using Docker Compose:**

   ```bash
   docker-compose up --build

2. **Run the tests:**

   ```bash
   docker-compose run web pytest
## Running Tests

This project uses `pytest` for testing. The test suite covers various aspects of the application, including unit tests, integration tests, and functional tests. Below are the key components of the test suite:

### Test Suite Components

- **`conftest.py`**: Contains the test fixtures used for setting up the application context, client, and database for testing.

- **Unit Tests**: Focus on individual components, such as models and utility functions.
  - **Example**: Testing the creation of a user, verifying password hashing, or checking the status of a task.

- **Integration Tests**: Test how different parts of the application work together, involving the database and other components.
  - **Example**: Testing the entire user registration process from form submission to checking if the user exists in the database.

- **Functional Tests**: Simulate real user scenarios, such as logging in, creating a task, sharing a task, etc.
  - **Example**: Testing the task creation flow by submitting a new task and verifying it shows up in the task list.

### Running the Tests
To run the test suite, use the following command (at the root):

`pytest`  

## Architectural Design

The project follows a modular and scalable design, which makes it easy to extend and maintain. The key components include:

- **Flask Blueprints**: The application is divided into blueprints, separating different concerns like authentication, task management, and admin functionalities. This separation allows for easier management and scaling of the application.

- **Models**: The application uses SQLAlchemy models to represent the database structure. Key models include `User`, `Task`, and `Permission`. Each model is responsible for its own business logic, such as verifying passwords or managing task statuses.

- **Routes and Views**: The routes are organized in the `routes.py` file and are responsible for handling HTTP requests and rendering templates or returning JSON responses. Admin routes are separated and protected by the `@admin_required` decorator.

- **Templates**: The HTML templates are stored in the `templates/` directory and follow the Jinja2 templating engine. These templates are structured to allow for easy customization and reuse of common components like headers, footers, and navigation menus.

- **Utilities**: Utility functions and decorators, such as `admin_required`, are placed in the `utils.py` file. This keeps the routes and views clean and focused on their primary responsibilities.

### Database Structure

This project uses **SQLite** as its primary database during development. The database interactions are managed using **SQLAlchemy**, which is an Object-Relational Mapping (ORM) tool that allows for a more intuitive and Pythonic way to work with databases.

#### ORM (Object-Relational Mapping)

**SQLAlchemy** is used as the ORM to interact with the database. It allows you to define models as Python classes, which are then mapped to database tables. This abstraction layer helps in writing cleaner and more maintainable code without the need to write raw SQL queries.

#### Models

The following models are defined in the project:

- **User**: Represents the users of the application. This model includes fields for storing the username, password (hashed), and admin status.
  
- **Task**: Represents tasks created by users. It includes fields for the task title, description, status, and the user to whom the task belongs.
  
- **Permission**: Represents the permissions associated with tasks. It tracks which users can view or edit tasks shared with them.

#### Relationships

- **One-to-Many Relationship**: 
  - **User** ↔ **Task**: A single user can own multiple tasks. This relationship is established using a foreign key in the `Task` model that references the `User` model.
  
- **Many-to-Many Relationship**: 
  - **User** ↔ **Task** (via **Permission**): Tasks can be shared with multiple users, and users can have permissions on multiple tasks. This is managed through the `Permission` model, which acts as an associative table between `User` and `Task`.

#### Migrations
To create and apply migrations, use the following commands:

      flask db init      # Initialize the migrations directory
      flask db migrate   # Generate a new migration script
      flask db upgrade   # Apply the migration to the database

## API Endpoints

The application provides the following key API endpoints:

- **GET /**: Home page. Redirects to the tasks page if the user is authenticated.
- **GET /login**: Displays the login form.
- **POST /login**: Handles user login.
- **GET /logout**: Logs out the current user.
- **GET /register**: Displays the registration form.
- **POST /register**: Handles user registration.
- **GET /tasks**: Displays the list of tasks for the logged-in user.
- **GET /task/new**: Displays the form to create a new task.
- **POST /task/new**: Handles the creation of a new task.
- **GET /task/edit/<int:task_id>**: Displays the form to edit an existing task.
- **POST /task/edit/<int:task_id>**: Handles the editing of an existing task.
- **POST /task/share/<int:task_id>**: Shares a task with another user.
- **POST /task/update_status/<int:task_id>**: Updates the status of a task.
- **POST /task/delete/<int:task_id>**: Deletes a task.

### Admin Routes

- **GET /admin/users**: Displays the list of all users (admin only).
- **POST /admin/toggle_admin/<int:user_id>**: Toggles the admin status of a user.
- **GET /admin/tasks**: Displays the list of all tasks (admin only).
- **POST /admin/edit_task/<int:task_id>**: Allows the admin to edit a task.
- **POST /admin/delete_task/<int:task_id>**: Allows the admin to delete a task.
- **POST /admin/delete_user/<int:user_id>**: Allows the admin to delete a user.

## Deployment

For deployment, you can use Docker to build and run the application in a containerized environment.
