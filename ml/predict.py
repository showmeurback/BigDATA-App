import joblib
import pandas as pd

def make_prediction(model_path, input_data):
    # Загрузка модели и имен фичей
    model, feature_names = joblib.load(model_path)

    # Преобразование входных данных в DataFrame
    df = pd.DataFrame([input_data])

    # Обработка категориальных данных (должно соответствовать тренировке)
    df_encoded = pd.get_dummies(df, drop_first=True)

    # Выравнивание колонок по тренировочным
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[feature_names]

    # Предсказание
    prediction = model.predict(df_encoded)
    return prediction[0]