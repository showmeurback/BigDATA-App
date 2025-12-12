from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import pandas as pd
from models import db, User, Dataset, Model, Status, ProjectType
from ml.train_model import train_model
from ml.predict import make_prediction

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))
        flash('Неверные учетные данные')
    return render_template('login.html')

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна')
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@routes.route('/dashboard')
@login_required
def dashboard():
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    models = Model.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', datasets=datasets, models=models)

@routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.csv', '.xlsx')):
            filename = secure_filename(file.filename)
            filepath = os.path.join('static', 'uploads', filename)
            file.save(filepath)
            dataset = Dataset(filename=filename, filepath=filepath, user_id=current_user.id)
            db.session.add(dataset)
            db.session.commit()
            flash('Файл загружен успешно')
            return redirect(url_for('routes.dashboard'))
        flash('Неверный формат файла')
    return render_template('upload.html')

@routes.route('/train/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def train(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    if dataset.user_id != current_user.id:
        flash('Доступ запрещен')
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        target_column = request.form.get('target_column')
        model_type = request.form.get('model_type')
        model_name = request.form.get('model_name')
        status_id = request.form.get('status_id')
        project_type_id = request.form.get('project_type_id')

        # Загрузка данных
        if dataset.filename.endswith('.csv'):
            df = pd.read_csv(dataset.filepath)
        else:
            df = pd.read_excel(dataset.filepath)

        # Тренировка модели
        model_path = train_model(df, target_column, model_type, model_name)
        model = Model(name=model_name, model_type=model_type, target_column=target_column, filepath=model_path, dataset_id=dataset_id, user_id=current_user.id, status_id=status_id, project_type_id=project_type_id)
        db.session.add(model)
        db.session.commit()
        flash('Модель обучена')
        return redirect(url_for('routes.dashboard'))

    # Получение колонок для выбора target
    if dataset.filename.endswith('.csv'):
        df = pd.read_csv(dataset.filepath)
    else:
        df = pd.read_excel(dataset.filepath)
    columns = df.columns.tolist()
    statuses = Status.query.all()
    project_types = ProjectType.query.all()
    return render_template('train.html', dataset=dataset, columns=columns, statuses=statuses, project_types=project_types)

@routes.route('/predict/<int:model_id>', methods=['GET', 'POST'])
@login_required
def predict(model_id):
    model = Model.query.get_or_404(model_id)
    if model.user_id != current_user.id:
        flash('Доступ запрещен')
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        # Получение данных для предсказания
        input_data = {}
        for key, value in request.form.items():
            if key != 'submit':
                input_data[key] = value  # Не конвертируем в float, чтобы поддерживать текст

        prediction = make_prediction(model.filepath, input_data)
        return render_template('predict.html', model=model, prediction=prediction, input_data=input_data)

    # Получение фичей модели
    dataset = model.dataset
    if dataset.filename.endswith('.csv'):
        df = pd.read_csv(dataset.filepath)
    else:
        df = pd.read_excel(dataset.filepath)
    # Исключаем target column
    features = [col for col in df.columns if col != model.target_column]
    return render_template('predict.html', model=model, features=features)