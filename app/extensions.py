from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect


# Database
db = SQLAlchemy()

# Login management
login_manager = LoginManager()

# CSRF protection
csrf = CSRFProtect()