from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor, CKEditorField


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
