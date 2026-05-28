"""
FoodBridge ML Model - Surplus Prediction
Training script to generate and save the model
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_data(n_samples=500):
    """
    Generate synthetic donation records with realistic patterns
    - Friday evenings in Zone A have higher surplus
    - Saturday mornings in Zone B have moderate surplus
    - Zone C has lower surplus generally
    - End of month has higher surplus (inventory clearance)
    """
    zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    categories = ['Cooked', 'Raw', 'Packaged']
    months = list(range(1, 13))

    data = []

    for _ in range(n_samples):
        zone = random.choice(zones)
        day = random.choice(days_of_week)
        hour = random.randint(8, 22)  # 8 AM to 10 PM
        category = random.choice(categories)
        month = random.choice(months)

        # Base quantity with some noise
        base_quantity = random.gauss(15, 5)  # Mean 15kg, std 5kg

        # Add patterns
        multiplier = 1.0

        # Friday evening in Zone A = high surplus (restaurants, events)
        if day == 'Friday' and hour >= 17 and zone == 'Zone A':
            multiplier *= 2.5
        elif day == 'Friday' and hour >= 17 and zone == 'Zone D':
            multiplier *= 2.0

        # Saturday morning in Zone B = moderate surplus (grocery stores)
        if day == 'Saturday' and 8 <= hour <= 12 and zone == 'Zone B':
            multiplier *= 1.8

        # Sunday = lower activity
        if day == 'Sunday':
            multiplier *= 0.6

        # Zone C = generally lower surplus
        if zone == 'Zone C':
            multiplier *= 0.7

        # End of month (days 28-31) = higher due to inventory clearance
        if month in [1, 3, 5, 7, 8, 10, 12]:  # Months with 31 days
            multiplier *= 1.3

        # Evening hours = higher surplus
        if hour >= 17:
            multiplier *= 1.4

        # Late night = lower
        if hour >= 21:
            multiplier *= 0.5

        # Cooked food has shorter shelf life, posted more urgently
        if category == 'Cooked':
            multiplier *= 1.2

        quantity = max(1, base_quantity * multiplier + random.gauss(0, 3))

        data.append({
            'zone': zone,
            'day_of_week': day,
            'hour': hour,
            'category': category,
            'month': month,
            'quantity': round(quantity, 2)
        })

    return pd.DataFrame(data)


def train_model():
    """Train the Random Forest model and save it"""

    print("Generating synthetic data...")
    df = generate_synthetic_data(500)

    # Save dataset to CSV
    os.makedirs('ml', exist_ok=True)
    df.to_csv('ml/dataset.csv', index=False)
    print(f"Dataset saved: {len(df)} records")

    # Encode categorical variables
    le_zone = LabelEncoder()
    le_day = LabelEncoder()
    le_category = LabelEncoder()

    df['zone_encoded'] = le_zone.fit_transform(df['zone'])
    df['day_encoded'] = le_day.fit_transform(df['day_of_week'])
    df['category_encoded'] = le_category.fit_transform(df['category'])

    # Features and target
    features = ['zone_encoded', 'day_encoded', 'hour', 'category_encoded', 'month']
    X = df[features]
    y = df['quantity']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    print(f"\nModel Performance:")
    print(f"  Training R² Score: {train_score:.4f}")
    print(f"  Test R² Score: {test_score:.4f}")

    # Save model and encoders
    model_data = {
        'model': model,
        'le_zone': le_zone,
        'le_day': le_day,
        'le_category': le_category
    }

    with open('ml/model.pkl', 'wb') as f:
        pickle.dump(model_data, f)

    print(f"\nModel saved to ml/model.pkl")

    # Print feature importances
    importances = model.feature_importances_
    feature_names = ['Zone', 'Day of Week', 'Hour', 'Category', 'Month']
    print("\nFeature Importances:")
    for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {importance:.4f}")

    return model, test_score


def categorize_surplus(quantity):
    """Categorize predicted quantity into surplus level"""
    if quantity >= 25:
        return 'High'
    elif quantity >= 15:
        return 'Medium'
    else:
        return 'Low'


if __name__ == '__main__':
    model, accuracy = train_model()
    print(f"\n{'='*50}")
    print(f"ML Model Training Complete")
    print(f"Accuracy: {accuracy:.1%}")
    print(f"{'='*50}")
