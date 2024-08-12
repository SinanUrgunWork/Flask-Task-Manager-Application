import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

load_dotenv()

# Initialize the database instance
db = SQLAlchemy()

# Initialize the login manager instance
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)

    if config_name:
        app.config.from_object(config_name)
    else:
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Ensure this is correctly prefixed

    migrate = Migrate(app, db)

    # Import and register the main Blueprint for organizing routes
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # User loader function used by Flask-Login to load a user by ID
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))  # Fetch the user from the database by ID

    # Ensure that all necessary database tables are created before the app runs
    with app.app_context():
        db.create_all()

    return app
