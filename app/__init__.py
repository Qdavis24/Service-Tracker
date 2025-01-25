from flask import Flask
from .models import Users
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from .extensions import db, login_manager, migrate
from .config import Config
# blueprints
from .views import main_bp, api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    db.init_app(app)
    app.config['CKEDITOR_SERVE_LOCAL'] = True
    app.config['CKEDITOR_PKG_TYPE'] = 'standard'
    app.config['CKEDITOR_VERSION'] = '4.24.0'
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()
    login_manager.init_app(app)
    ckeditor = CKEditor(app)
    csrf = CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    return app
