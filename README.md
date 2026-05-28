# FoodBridge - Food Waste & Hunger Platform

A full-stack web application that connects food donors with receivers (NGOs/orphanages), featuring an ML-powered surplus prediction system.

## Features

- **Home Page** - Emotional hero section, live stats counter, how-it-works guide, testimonials
- **Donor Dashboard** - Post food donations, view/edit/delete listings, see impact stats
- **Receiver Dashboard** - Browse available food by zone/category, claim donations, view pickup details
- **Admin Panel** - Manage users, listings, claims; view ML predictions; export data
- **ML Prediction** - Random Forest model predicting food surplus by zone and day

## Tech Stack

- **Backend**: Python 3.11 + Flask + Gunicorn (production WSGI)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Frontend**: HTML, CSS, Bootstrap 5
- **Auth**: Flask-Login with session-based authentication
- **ML**: scikit-learn (Random Forest), pandas, numpy
- **Charts**: Chart.js for admin dashboard
- **Deployment**: Railway / Render with automatic Git-based deployment

## Project Structure

```
FoodBridge/
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy database models
├── requirements.txt        # Python dependencies
├── routes/
│   ├── auth.py             # Authentication routes
│   ├── donor.py            # Donor API routes
│   ├── receiver.py         # Receiver API routes
│   └── admin.py            # Admin API routes
├── ml/
│   ├── model.py            # ML training script
│   ├── predict.py          # Prediction functions
│   ├── model.pkl           # Trained model (generated)
│   └── dataset.csv         # Training data (generated)
├── static/
│   ├── css/style.css       # Custom styles
│   ├── js/main.js          # Frontend JavaScript
│   └── uploads/            # Food images
└── templates/
    ├── base.html           # Base layout
    ├── index.html           # Home page
    ├── donor.html           # Donor dashboard
    ├── receiver.html        # Receiver dashboard
    ├── admin.html           # Admin dashboard
    ├── about.html           # About page
    ├── login.html           # Login page
    └── register.html        # Registration page
```

## Setup Instructions

### Local Development

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Train the ML Model

```bash
python ml/model.py
```

This creates `ml/model.pkl` and `ml/dataset.csv` with synthetic training data.

#### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

#### 4. Demo Accounts

- **Admin**: admin@foodbridge.org / admin123

Register as a donor or receiver from the registration page.

### Production Deployment (Railway / Render)

#### 1. Prerequisites
- GitHub account with repository
- Railway.app or Render.com account (free tier available)

#### 2. Deploy to Railway (Recommended)

1. Push code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add environment variables:
   - `SECRET_KEY`: Generate a strong secret key
   - `DATABASE_URL`: PostgreSQL connection string (Railway provides automatic PostgreSQL)
   - `FLASK_ENV`: Set to `production`
6. Railway automatically detects the `Procfile` and deploys
7. Your app gets a live URL immediately

#### 3. Deploy to Render (Alternative)

1. Push code to GitHub
2. Go to [Render.com](https://render.com)
3. Click "New" → "Web Service"
4. Select your GitHub repository
5. Configure:
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt && python ml/model.py`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
6. Add PostgreSQL database from Render dashboard
7. Set environment variables (DATABASE_URL auto-configured)
8. Click "Create Web Service"
9. Your live URL appears in the dashboard

#### 4. Environment Variables Required
```
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql://...provided-by-railway-or-render...
FLASK_ENV=production
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register donor or receiver |
| POST | `/api/login` | Login and create session |
| GET | `/api/logout` | Logout user |
| GET | `/api/listings` | Get all available food listings |
| POST | `/api/listings` | Donor posts new food listing |
| PUT | `/api/listings/<id>` | Donor edits listing |
| DELETE | `/api/listings/<id>` | Donor deletes listing |
| POST | `/api/claim/<id>` | Receiver claims a listing |
| GET | `/api/admin/users` | Admin gets all users |
| GET | `/api/admin/stats` | Admin gets platform stats |
| GET | `/api/predict` | ML surplus prediction |
| POST | `/api/contact` | Save contact form message |
| GET | `/api/admin/export/users` | Export users CSV |
| GET | `/api/admin/export/listings` | Export listings CSV |

## Database Models

### User
- id, name, email, password_hash, role (donor/receiver/admin)
- phone, address, zone, registration_number
- is_verified, created_at

### FoodListing
- id, donor_id, food_name, quantity, category
- expiry_time, pickup_address, zone, description
- image_path, status (available/claimed/expired), created_at

### Claim
- id, listing_id, receiver_id, status, claimed_at

### DonationRecord
- id, zone, day_of_week, hour, quantity, category, month
- Used for ML training

## ML Model Details

- **Algorithm**: Random Forest Regressor
- **Features**: zone, day_of_week, hour, category, month
- **Target**: quantity (surplus amount)
- **Training Data**: 500+ synthetic records with realistic patterns
- **Accuracy**: ~84% R² score on test data

The model predicts:
- High surplus on Friday evenings in Zone A (restaurants)
- Moderate surplus on Saturday mornings in Zone B (grocery stores)
- Zone C has generally lower surplus
- End of month shows increased activity

## Design

- **Color Theme**: Green (#2e7d32) and Orange (#f57c00)
- **UI Framework**: Bootstrap 5
- **Mobile-first**: Fully responsive design
- **Animations**: Subtle hover effects and transitions

## Development Log

| Date | Milestone |
|------|-----------|
| May 7 | Donor Registration page completed |
| May 9 | Random Forest model trained - 84% accuracy |
| May 12 | Flask backend with CRUD operations completed |
| May 15 | Admin dashboard with ML predictions integrated |
| May 20 | Full integration testing done |

## License

MIT License - Feel free to use this project for educational or commercial purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
