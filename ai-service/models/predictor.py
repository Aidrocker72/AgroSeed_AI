import pandas as pd
import numpy as np
from collections import deque
from datetime import timedelta
from typing import List, Dict, Any
import joblib
import os
from xgboost import XGBRegressor
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
        self.is_trained = False

        os.makedirs(model_storage_path, exist_ok=True)

    @staticmethod
    def _build_rate_map(exchange_rates: List[Dict[str, Any]]) -> Dict[str, float]:
        """date_str → usd_rub_rate lookup table."""
        if not exchange_rates:
            return {}
        return {r["date"]: float(r["rate"]) for r in exchange_rates}

    def _prepare_data(
        self,
        seed_data: List[Dict[str, Any]],
        exchange_rates: List[Dict[str, Any]] | None = None,
        oil_prices: List[Dict[str, Any]] | None = None,
    ) -> pd.DataFrame:
        df = pd.DataFrame(seed_data)
        df['date'] = pd.to_datetime(df['date'])
        df = (df.sort_values('date')
                .drop_duplicates(subset=['date'], keep='last')
                .reset_index(drop=True))

        # Календарные фичи
        df['year']        = df['date'].dt.year
        df['month']       = df['date'].dt.month
        df['day']         = df['date'].dt.day
        df['day_of_year'] = df['date'].dt.dayofyear
        df['day_of_week'] = df['date'].dt.dayofweek
        # Синус/косинус для циклической сезонности
        df['month_sin']   = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos']   = np.cos(2 * np.pi * df['month'] / 12)

        # Lag-фичи — лучше RF'у улавливать автокорреляцию
        # fillna первым значением: при коротком ряде shift(N) даёт N NaN-строк
        first_price = float(df['price'].iloc[0])
        df['price_lag_1']  = df['price'].shift(1).fillna(first_price)
        df['price_lag_7']  = df['price'].shift(7).fillna(first_price)
        df['price_lag_30'] = df['price'].shift(30).fillna(first_price)
        df['price_lag_90'] = df['price'].shift(90).fillna(first_price)

        # Скользящие средние
        df['price_ma_7']  = df['price'].rolling(7,  min_periods=1).mean()
        df['price_ma_14'] = df['price'].rolling(14, min_periods=1).mean()
        df['price_ma_30'] = df['price'].rolling(30, min_periods=1).mean()

        # Изменение и волатильность
        df['price_change']     = df['price'].pct_change().fillna(0)
        df['price_volatility'] = df['price_change'].rolling(7, min_periods=1).std().fillna(0)

        # Курс USD/RUB: присоединяем по дате, заполняем пропуски соседними значениями
        rate_map = self._build_rate_map(exchange_rates or [])
        df['usd_rub_rate'] = df['date'].dt.date.astype(str).map(rate_map)
        df['usd_rub_rate'] = df['usd_rub_rate'].ffill().bfill().fillna(90.0)

        # Цена нефти Brent (USD/барр.): топливо → транспорт → цена семян
        oil_map = self._build_rate_map(oil_prices or [])
        df['oil_price_usd'] = df['date'].dt.date.astype(str).map(oil_map)
        df['oil_price_usd'] = df['oil_price_usd'].ffill().bfill().fillna(75.0)

        # Sentiment (заглушка — данные есть, NLP в следующей итерации)
        df['news_count']     = 0
        df['sentiment_score'] = 0.0

        return df.ffill().bfill()

    def train(
        self,
        seed_data: List[Dict[str, Any]],
        news_data: List[Dict[str, Any]],  # noqa: ARG002
        exchange_rates: List[Dict[str, Any]] | None = None,
        oil_prices: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        df = self._prepare_data(seed_data, exchange_rates, oil_prices)

        if len(df) < 10:
            raise ValueError("Недостаточно данных для обучения (минимум 10 точек)")

        feature_columns = [
            'year', 'month', 'day', 'day_of_year', 'day_of_week',
            'month_sin', 'month_cos',
            'price_lag_1', 'price_lag_7', 'price_lag_30', 'price_lag_90',
            'price_ma_7', 'price_ma_14', 'price_ma_30',
            'price_change', 'price_volatility',
            'usd_rub_rate', 'oil_price_usd',
            'news_count', 'sentiment_score',
        ]

        df_clean = df.dropna(subset=feature_columns)
        if len(df_clean) < 10:
            raise ValueError("Недостаточно данных после очистки")

        X = df_clean[feature_columns]
        y = df_clean['price']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )

        self.price_model = XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=42, n_jobs=-1, verbosity=0,
        )
        self.price_model.fit(X_train, y_train)

        y_pred = self.price_model.predict(X_test)
        mae  = mean_absolute_error(y_test, y_pred)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

        # Holt-Winters — годовая сезонность если данных достаточно
        series = df.set_index('date')['price'].asfreq('D').ffill()
        sp = min(365, len(series) // 2)
        try:
            if len(series) >= sp * 2 and sp > 1:
                self.trend_model = ExponentialSmoothing(
                    series, trend='add', seasonal='add', seasonal_periods=sp
                ).fit(optimized=True)
            else:
                self.trend_model = ExponentialSmoothing(
                    series, trend='add'
                ).fit(optimized=True)
        except Exception:
            self.trend_model = ExponentialSmoothing(series).fit(optimized=True)

        self.is_trained = True
        self._feature_columns = feature_columns

        return {
            "model_type": "RandomForest + ExponentialSmoothing",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "features_used": feature_columns,
        }

    def predict(
        self,
        seed_data: List[Dict[str, Any]],
        news_data: List[Dict[str, Any]],  # noqa: ARG002
        forecast_period: int = 30,
        exchange_rates: List[Dict[str, Any]] | None = None,
        oil_prices: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        if not self.is_trained:
            raise ValueError("Модель не обучена. Сначала выполните обучение.")

        df = self._prepare_data(seed_data, exchange_rates, oil_prices)
        current_date = df['date'].max()
        future_dates = [current_date + timedelta(days=i) for i in range(1, forecast_period + 1)]

        # HW прогноз
        hw_forecast = self.trend_model.forecast(forecast_period)
        hw_values   = hw_forecast.values
        residuals_std = float(np.std(self.trend_model.resid)) if hasattr(self.trend_model, 'resid') else float(df['price'].std() * 0.1)

        # Буфер последних 90 цен для рекурсивного обновления фичей
        price_buf = deque(df['price'].values[-90:], maxlen=90)

        # Последние известные значения — для будущих дат используем их как константы
        last_rate     = float(df['usd_rub_rate'].iloc[-1])
        last_oil      = float(df['oil_price_usd'].iloc[-1])

        forecast_data = []
        upper_bound   = []
        lower_bound   = []

        for i, date in enumerate(future_dates):
            buf = list(price_buf)

            lag_1  = buf[-1]
            lag_7  = buf[-7]  if len(buf) >= 7  else buf[0]
            lag_30 = buf[-30] if len(buf) >= 30 else buf[0]
            lag_90 = buf[-90] if len(buf) >= 90 else buf[0]

            ma_7  = float(np.mean(buf[-7:]))
            ma_14 = float(np.mean(buf[-14:])) if len(buf) >= 14 else float(np.mean(buf))
            ma_30 = float(np.mean(buf[-30:])) if len(buf) >= 30 else float(np.mean(buf))

            prev_price    = buf[-2] if len(buf) >= 2 else buf[-1]
            price_change  = (lag_1 - prev_price) / prev_price if prev_price else 0.0
            price_volatility = float(np.std(buf[-7:])) / lag_1 if lag_1 and len(buf) >= 7 else 0.0

            features = pd.DataFrame([{
                'year':            date.year,
                'month':           date.month,
                'day':             date.day,
                'day_of_year':     date.timetuple().tm_yday,
                'day_of_week':     date.weekday(),
                'month_sin':       np.sin(2 * np.pi * date.month / 12),
                'month_cos':       np.cos(2 * np.pi * date.month / 12),
                'price_lag_1':     lag_1,
                'price_lag_7':     lag_7,
                'price_lag_30':    lag_30,
                'price_lag_90':    lag_90,
                'price_ma_7':      ma_7,
                'price_ma_14':     ma_14,
                'price_ma_30':     ma_30,
                'price_change':    price_change,
                'price_volatility': price_volatility,
                'usd_rub_rate':    last_rate,
                'oil_price_usd':   last_oil,
                'news_count':      0,
                'sentiment_score': 0.0,
            }])

            rf_pred = float(self.price_model.predict(features)[0])
            hw_pred = float(hw_values[i])

            # RF точнее на коротком горизонте, HW берёт тренд на длинном
            weight   = 1.0 - (i / forecast_period) * 0.4
            combined = weight * rf_pred + (1 - weight) * hw_pred

            # Обновляем буфер предсказанным значением
            price_buf.append(combined)

            z      = 1.96
            margin = z * residuals_std * np.sqrt(i + 1)

            forecast_data.append({
                "date":            date.strftime('%Y-%m-%d'),
                "predicted_price": round(combined, 2),
                "rf_prediction":   round(rf_pred, 2),
                "hw_prediction":   round(hw_pred, 2),
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
                "model_type":       "RandomForest + ExponentialSmoothing",
                "forecast_period":  forecast_period,
                "last_known_price": round(float(df['price'].iloc[-1]), 2),
                "last_known_date":  df['date'].iloc[-1].strftime('%Y-%m-%d'),
            },
        }

    def save_model(self, model_name: str = "price_predictor"):
        if not self.is_trained:
            raise ValueError("Модель не обучена.")
        path = os.path.join(self.model_storage_path, f"{model_name}.joblib")
        joblib.dump({
            'model':            self.price_model,
            'trend_model':      self.trend_model,
            'is_trained':       self.is_trained,
            'feature_columns':  getattr(self, '_feature_columns', []),
        }, path)
        return path

    def load_model(self, model_name: str = "price_predictor"):
        path = os.path.join(self.model_storage_path, f"{model_name}.joblib")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Модель {path} не найдена")
        data = joblib.load(path)
        self.price_model      = data['model']
        self.trend_model      = data['trend_model']
        self.is_trained       = data['is_trained']
        self._feature_columns = data.get('feature_columns', [])
        return True
