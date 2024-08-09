from flask import Flask
from sqlalchemy.testing.pickleable import User
from .models import Users
from flask_ckeditor import CKEditor, CKEditorField
from .extensions import db, login_manager, migrate
from .config import Config
# blueprints
from .views import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main_bp)
    db.init_app(app)
    app.config['CKEDITOR_SERVE_LOCAL'] = True
    app.config['CKEDITOR_PKG_TYPE'] = 'standard'
    app.config['CKEDITOR_VERSION'] = '4.24.0'
    migrate.init_app(app, db)
    login_manager.init_app(app)
    ckeditor = CKEditor(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    return app
