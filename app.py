from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User, Status, ProjectType
import routes
import os

os.environ['FLASK_ENV'] = 'development'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'routes.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(routes.routes)

    with app.app_context():
        db.create_all()
        # Добавление начальных данных
        if not Status.query.first():
            statuses = ['В работе', 'Завершена', 'Ошибка']
            for s in statuses:
                db.session.add(Status(name=s))
        if not ProjectType.query.first():
            types = ['Анализ данных', 'ML проект', 'Визуализация']
            for t in types:
                db.session.add(ProjectType(name=t))
        db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)