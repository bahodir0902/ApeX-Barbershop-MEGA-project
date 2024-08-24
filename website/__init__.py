from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

db = SQLAlchemy()
DB_NAME = 'database.db'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql:///{DB_NAME}"

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .permissions import permissions
    from .barber_page import barber_page

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(permissions, url_prefix='/')
    app.register_blueprint(barber_page, url_prefix='/')

    from .models import User
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)


    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    return app

