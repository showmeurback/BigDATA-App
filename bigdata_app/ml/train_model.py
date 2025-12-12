import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import os

def train_model(df, target_column, model_type, model_name):
    # Разделение на features и target
    X = df.drop(columns=[target_column])
    y = df[target_column]
    # Обработка пропущенных значений
    combined = pd.concat([X, y], axis=1)
    combined = combined.dropna()
    X = combined.drop(columns=[target_column])
    y = combined[target_column]
    # Обработка категориальных данных (простая версия)
    X_encoded = pd.get_dummies(X, drop_first=True)
    feature_names = X_encoded.columns.tolist()

    # Разделение на train/test
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

    # Выбор модели
    if model_type == 'regression':
        if 'linear' in model_name.lower():
            model = LinearRegression()
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
    else:  # classification
        if 'logistic' in model_name.lower():
            model = LogisticRegression(max_iter=1000)
        else:
            model = RandomForestClassifier(n_estimators=100, random_state=42)

    # Тренировка
    model.fit(X_train, y_train)

    # Оценка
    predictions = model.predict(X_test)
    if model_type == 'regression':
        score = mean_squared_error(y_test, predictions)
        print(f'MSE: {score}')
    else:
        score = accuracy_score(y_test, predictions)
        print(f'Accuracy: {score}')

    # Сохранение модели
    model_path = os.path.join('ml', 'models', f'{model_name}.pkl')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump((model, feature_names), model_path)

    return model_path