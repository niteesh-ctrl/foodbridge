"""
FoodBridge ML Prediction
Load trained model and generate predictions
"""

import pickle
import os
from datetime import datetime
import numpy as np

# Load model and encoders
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

_model = None
_le_zone = None
_le_day = None
_le_category = None


def load_model():
    """Load the trained model from disk"""
    global _model, _le_zone, _le_day, _le_category

    if not os.path.exists(MODEL_PATH):
        print("Warning: Model not found. Run 'python ml/model.py' to train the model first.")
        return False

    with open(MODEL_PATH, 'rb') as f:
        data = pickle.load(f)

    _model = data['model']
    _le_zone = data['le_zone']
    _le_day = data['le_day']
    _le_category = data['le_category']

    return True


def categorize_surplus(quantity):
    """Categorize predicted quantity into surplus level"""
    if quantity >= 25:
        return 'High'
    elif quantity >= 15:
        return 'Medium'
    else:
        return 'Low'


def predict_surplus(zone, day_of_week, hour, category, month):
    """Predict surplus quantity for given parameters"""

    global _model, _le_zone, _le_day, _le_category

    # Load model if not already loaded
    if _model is None:
        if not load_model():
            # Return default predictions if model not available
            return 15.0

    try:
        zone_encoded = _le_zone.transform([zone])[0]
        day_encoded = _le_day.transform([day_of_week])[0]
        category_encoded = _le_category.transform([category])[0]
    except ValueError:
        # Handle unseen labels
        return 12.0

    features = np.array([[zone_encoded, day_encoded, hour, category_encoded, month]])
    prediction = _model.predict(features)

    return max(0, prediction[0])


def get_predictions():
    """Get surplus predictions for all zones for upcoming days"""

    # Days to predict
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
    categories = ['Cooked', 'Raw', 'Packaged']

    current_month = datetime.now().month
    current_hour = datetime.now().hour

    predictions = []

    for zone in zones:
        for day in days:
            # Predict for evening hours (high surplus period)
            max_prediction = 0

            for hour in range(17, 22):  # 5 PM to 10 PM
                for category in ['Cooked']:  # Primary category for events
                    pred = predict_surplus(zone, day, hour, category, current_month)
                    max_prediction = max(max_prediction, pred)

            surplus_level = categorize_surplus(max_prediction)

            # Update to use formatted zone name
            predictions.append({
                'zone': zone,
                'day': day,
                'predicted_quantity': round(max_prediction, 1),
                'predicted_surplus': surplus_level
            })

    return predictions


def get_chart_data():
    """Get prediction data formatted for Chart.js"""

    predictions = get_predictions()

    # Group by zone
    zone_data = {}
    for p in predictions:
        zone = p['zone']
        if zone not in zone_data:
            zone_data[zone] = {'High': 0, 'Medium': 0, 'Low': 0}
        zone_data[zone][p['predicted_surplus']] += 1

    # Count surplus levels per zone
    zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
    high_counts = [zone_data[z]['High'] if z in zone_data else 0 for z in zones]
    medium_counts = [zone_data[z]['Medium'] if z in zone_data else 0 for z in zones]
    low_counts = [zone_data[z]['Low'] if z in zone_data else 0 for z in zones]

    return {
        'labels': zones,
        'datasets': [
            {
                'label': 'High Surplus',
                'data': high_counts,
                'backgroundColor': '#f44336'
            },
            {
                'label': 'Medium Surplus',
                'data': medium_counts,
                'backgroundColor': '#ff9800'
            },
            {
                'label': 'Low Surplus',
                'data': low_counts,
                'backgroundColor': '#4caf50'
            }
        ]
    }


# Initialize model on module load
load_model()
