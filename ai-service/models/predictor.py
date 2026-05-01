import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List, Dict, Any
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings('ignore')


class PricePredictor:
    def __init__(self, model_storage_path: str = "./models"):
        self.model_storage_path = model_storage_path
        self.price_model = None
        self.trend_model = None
        self.scaler = StandardScaler()
        self.is_trained = False

        os.makedirs(model_storage_path, exist_ok=True)

    def _prepare_data(self, seed_data: List[Dict[str, Any]], news_data: List[Dict[str, Any]] = None) -> pd.DataFrame:  # noqa: ARG002
        df = pd.DataFrame(seed_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').drop_duplicates(subset=['date'], keep='last').reset_index(drop=True)

        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_year'] = df['date'].dt.dayofyear
        df['day_of_week'] = df['date'].dt.dayofweek

        df['price_ma_7'] = df['price'].rolling(window=7, min_periods=1).mean()
        df['price_ma_14'] = df['price'].rolling(window=14, min_periods=1).mean()
        df['price_ma_30'] = df['price'].rolling(window=30, min_periods=1).mean()

        df['price_change'] = df['price'].pct_change().fillna(0)
        df['price_volatility'] = df['price_change'].rolling(window=7, min_periods=1).std().fillna(0)

        df['news_count'] = 0
        df['sentiment_score'] = 0.0

        df = df.ffill().bfill()
        return df

    def train(self, seed_data: List[Dict[str, Any]], news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        df = self._prepare_data(seed_data, news_data)

        if len(df) < 10:
            raise ValueError("Недостаточно данных для обучения модели (минимум 10 точек)")

        feature_columns = [
            'year', 'month', 'day', 'day_of_year', 'day_of_week',
            'price_ma_7', 'price_ma_14', 'price_ma_30',
            'price_change', 'price_volatility',
            'news_count', 'sentiment_score'
        ]

        df = df.dropna()
        if len(df) < 10:
            raise ValueError("Недостаточно данных после очистки")

        X = df[feature_columns]
        y = df['price']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.price_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.price_model.fit(X_train, y_train)

        y_pred = self.price_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        # Holt-Winters для тренда и доверительных интервалов
        series = df.set_index('date')['price'].asfreq('D').ffill()
        seasonal_periods = min(7, len(series) // 2)
        try:
            if len(series) >= seasonal_periods * 2:
                self.trend_model = ExponentialSmoothing(
                    series,
                    trend='add',
                    seasonal='add',
                    seasonal_periods=seasonal_periods,
                ).fit(optimized=True)
            else:
                self.trend_model = ExponentialSmoothing(series, trend='add').fit(optimized=True)
        except Exception:
            self.trend_model = ExponentialSmoothing(series).fit(optimized=True)

        self.is_trained = True

        return {
            "model_type": "RandomForest + ExponentialSmoothing",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "features_used": feature_columns,
        }

    def predict(self, seed_data: List[Dict[str, Any]], news_data: List[Dict[str, Any]],
                forecast_period: int = 30) -> Dict[str, Any]:
        if not self.is_trained:
            raise ValueError("Модель не обучена. Сначала выполните обучение.")

        df = self._prepare_data(seed_data, news_data)
        last_row = df.iloc[-1]
        current_date = df['date'].max()

        future_dates = [current_date + timedelta(days=i) for i in range(1, forecast_period + 1)]

        # Holt-Winters прогноз
        hw_forecast = self.trend_model.forecast(forecast_period)
        hw_values = hw_forecast.values

        # Оценка стандартного отклонения остатков для доверительного интервала
        residuals_std = float(np.std(self.trend_model.resid)) if hasattr(self.trend_model, 'resid') else float(df['price'].std() * 0.1)

        forecast_data = []
        upper_bound = []
        lower_bound = []

        for i, date in enumerate(future_dates):
            future_features = pd.DataFrame([{
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'day_of_year': date.timetuple().tm_yday,
                'day_of_week': date.weekday(),
                'price_ma_7': last_row['price_ma_7'],
                'price_ma_14': last_row['price_ma_14'],
                'price_ma_30': last_row['price_ma_30'],
                'price_change': last_row['price_change'],
                'price_volatility': last_row['price_volatility'],
                'news_count': 0,
                'sentiment_score': 0.0,
            }])
            rf_pred = float(self.price_model.predict(future_features)[0])
            hw_pred = float(hw_values[i])

            # RF более релевантен на коротком горизонте, HW — на длинном
            weight = 1.0 - (i / forecast_period) * 0.4
            combined = weight * rf_pred + (1 - weight) * hw_pred

            z = 1.96  # 95% CI
            margin = z * residuals_std * np.sqrt(i + 1)

            forecast_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "predicted_price": round(combined, 2),
                "rf_prediction": round(rf_pred, 2),
                "hw_prediction": round(hw_pred, 2),
            })
            upper_bound.append(round(combined + margin, 2))
            lower_bound.append(round(combined - margin, 2))

        return {
            "forecast": forecast_data,
            "confidence_interval": {
                "upper_bound": upper_bound,
                "lower_bound": lower_bound,
            },
            "model_info": {
                "model_type": "RandomForest + ExponentialSmoothing",
                "forecast_period": forecast_period,
                "last_known_price": round(float(df['price'].iloc[-1]), 2),
                "last_known_date": df['date'].iloc[-1].strftime('%Y-%m-%d'),
            },
        }

    def save_model(self, model_name: str = "price_predictor"):
        if not self.is_trained:
            raise ValueError("Модель не обучена. Невозможно сохранить.")

        model_path = os.path.join(self.model_storage_path, f"{model_name}.joblib")
        joblib.dump({
            'model': self.price_model,
            'trend_model': self.trend_model,
            'is_trained': self.is_trained,
        }, model_path)
        return model_path

    def load_model(self, model_name: str = "price_predictor"):
        model_path = os.path.join(self.model_storage_path, f"{model_name}.joblib")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Модель {model_path} не найдена")

        model_data = joblib.load(model_path)
        self.price_model = model_data['model']
        self.trend_model = model_data['trend_model']
        self.is_trained = model_data['is_trained']
        return True
