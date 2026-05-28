"""
FoodBridge - Food Waste & Hunger Platform
Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models import db, User, FoodListing, Claim, ContactMessage, DonationRecord
from routes.auth import auth_bp
from routes.donor import donor_bp
from routes.receiver import receiver_bp
from routes.admin import admin_bp

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'foodbridge-secret-key-2024')

# Database configuration - supports both SQLite (local) and PostgreSQL (production)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Production: Use PostgreSQL from environment
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development: Use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foodbridge.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(donor_bp, url_prefix='/api')
app.register_blueprint(receiver_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============ PAGE ROUTES ============

@app.route('/')
def index():
    """Home page"""
    from ml.predict import get_predictions

    # Get live stats
    total_donations = FoodListing.query.count()
    meals_served = db.session.query(db.func.sum(FoodListing.quantity)).filter(
        FoodListing.status == 'claimed'
    ).scalar() or 0
    orphanages_helped = User.query.filter_by(role='receiver').count()

    # Get ML predictions
    predictions = get_predictions()

    return render_template('index.html',
        total_donations=total_donations,
        meals_served=int(meals_served * 4),  # Assume 1kg = 4 meals
        orphanages_helped=orphanages_helped,
        predictions=predictions
    )

@app.route('/donor')
@login_required
def donor():
    """Donor dashboard page"""
    if current_user.role != 'donor':
        flash('Access denied. Donor account required.', 'danger')
        return redirect(url_for('index'))

    # Get donor's donations
    donations_objs = FoodListing.query.filter_by(donor_id=current_user.id).order_by(
        FoodListing.created_at.desc()
    ).all()

    # Convert to JSON-serializable format for template
    donations_json = []
    for d in donations_objs:
        donations_json.append({
            'id': d.id,
            'food_name': d.food_name,
            'quantity': d.quantity,
            'category': d.category,
            'expiry_time': d.expiry_time.isoformat(),
            'pickup_address': d.pickup_address,
            'zone': d.zone,
            'description': d.description,
            'status': d.status,
            'created_at': d.created_at.isoformat() if d.created_at else ''
        })

    # Calculate impact
    total_meals = sum(d.quantity for d in donations_objs if d.status == 'claimed')

    return render_template('donor.html', donations=donations_objs, donations_json=donations_json, total_meals=total_meals * 4)

@app.route('/receiver')
@login_required
def receiver():
    """Receiver dashboard page"""
    if current_user.role != 'receiver':
        flash('Access denied. Receiver account required.', 'danger')
        return redirect(url_for('index'))

    # Get available listings (not expired, in same or nearby zone)
    listings = FoodListing.query.filter_by(status='available').order_by(
        FoodListing.created_at.desc()
    ).all()

    # Get receiver's claims
    claims = Claim.query.filter_by(receiver_id=current_user.id).order_by(
        Claim.claimed_at.desc()
    ).all()

    return render_template('receiver.html', listings=listings, claims=claims)

@app.route('/admin')
@login_required
def admin():
    """Admin dashboard page"""
    if current_user.role != 'admin':
        flash('Access denied. Admin account required.', 'danger')
        return redirect(url_for('index'))

    from ml.predict import get_predictions, get_chart_data

    # Get stats
    total_users = User.query.count()
    active_listings = FoodListing.query.filter_by(status='available').count()
    claims_today = Claim.query.filter(
        db.func.date(Claim.claimed_at) == db.func.date(db.func.current_timestamp())
    ).count()

    # Get all data
    users = User.query.all()
    listings = FoodListing.query.order_by(FoodListing.created_at.desc()).all()
    claims = Claim.query.order_by(Claim.claimed_at.desc()).all()

    predictions = get_predictions()
    chart_data = get_chart_data()

    return render_template('admin.html',
        total_users=total_users,
        active_listings=active_listings,
        claims_today=claims_today,
        users=users,
        listings=listings,
        claims=claims,
        predictions=predictions,
        chart_data=chart_data
    )

@app.route('/about')
def about():
    """About and contact page"""
    return render_template('about.html')

@app.route('/login')
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register')
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('register.html')

# ============ API ROUTES ============

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register donor or receiver"""
    data = request.get_json()

    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400

    # Create user
    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data['role'],
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        zone=data.get('zone', 'Zone A')
    )

    if data['role'] == 'receiver':
        user.registration_number = data.get('registration_number', '')

    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login and create session"""
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password_hash, data['password']):
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'role': user.role
        })

    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/api/logout')
@login_required
def api_logout():
    """Logout"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/listings', methods=['GET'])
def api_get_listings():
    """Get all available food listings"""
    listings = FoodListing.query.filter_by(status='available').order_by(
        FoodListing.expiry_time.asc()
    ).all()

    return jsonify({
        'success': True,
        'listings': [{
            'id': l.id,
            'food_name': l.food_name,
            'quantity': l.quantity,
            'category': l.category,
            'expiry_time': l.expiry_time.isoformat(),
            'pickup_address': l.pickup_address,
            'zone': l.zone,
            'description': l.description,
            'image_path': l.image_path,
            'donor_name': l.donor.name,
            'donor_phone': l.donor.phone
        } for l in listings]
    })

@app.route('/api/listings', methods=['POST'])
@login_required
def api_create_listing():
    """Donor posts new food listing"""
    if current_user.role != 'donor':
        return jsonify({'success': False, 'message': 'Only donors can post listings'}), 403

    try:
        data = request.get_json()

        expiry_str = data['expiry_time']
        if 'T' in expiry_str:
            expiry_dt = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        else:
            expiry_dt = datetime.strptime(expiry_str, '%Y-%m-%d %H:%M')

        listing = FoodListing(
            donor_id=current_user.id,
            food_name=data['food_name'],
            quantity=float(data['quantity']),
            category=data['category'],
            expiry_time=expiry_dt,
            pickup_address=data['pickup_address'],
            zone=data['zone'],
            description=data.get('description', '')
        )

        record = DonationRecord(
            zone=data['zone'],
            day_of_week=datetime.now().strftime('%A'),
            hour=datetime.now().hour,
            quantity=float(data['quantity']),
            category=data['category'],
            month=datetime.now().month
        )
        db.session.add(record)
        db.session.add(listing)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Food donation posted successfully!', 'id': listing.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error posting donation: {str(e)}'}), 400

@app.route('/api/listings/<int:id>', methods=['PUT'])
@login_required
def api_update_listing(id):
    """Donor edits listing"""
    listing = FoodListing.query.get_or_404(id)

    if listing.donor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()

    listing.food_name = data.get('food_name', listing.food_name)
    listing.quantity = float(data.get('quantity', listing.quantity))
    listing.category = data.get('category', listing.category)
    listing.expiry_time = datetime.fromisoformat(data['expiry_time']) if 'expiry_time' in data else listing.expiry_time
    listing.pickup_address = data.get('pickup_address', listing.pickup_address)
    listing.zone = data.get('zone', listing.zone)
    listing.description = data.get('description', listing.description)

    db.session.commit()

    return jsonify({'success': True, 'message': 'Listing updated'})

@app.route('/api/listings/<int:id>', methods=['DELETE'])
@login_required
def api_delete_listing(id):
    """Donor deletes listing"""
    listing = FoodListing.query.get_or_404(id)

    if listing.donor_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    db.session.delete(listing)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Listing deleted'})

@app.route('/api/claim/<int:id>', methods=['POST'])
@login_required
def api_claim_listing(id):
    """Receiver claims a listing"""
    if current_user.role != 'receiver':
        return jsonify({'success': False, 'message': 'Only receivers can claim listings'}), 403

    listing = FoodListing.query.get_or_404(id)

    if listing.status != 'available':
        return jsonify({'success': False, 'message': 'Listing no longer available'}), 400

    claim = Claim(
        listing_id=id,
        receiver_id=current_user.id
    )

    listing.status = 'claimed'

    db.session.add(claim)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Listing claimed successfully',
        'claim_id': claim.id
    })

@app.route('/api/admin/users')
@login_required
def api_admin_users():
    """Admin gets all users"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    users = User.query.all()

    return jsonify({
        'success': True,
        'users': [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'phone': u.phone,
            'zone': u.zone,
            'created_at': u.created_at.isoformat()
        } for u in users]
    })

@app.route('/api/admin/stats')
@login_required
def api_admin_stats():
    """Admin gets platform stats"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    return jsonify({
        'success': True,
        'stats': {
            'total_users': User.query.count(),
            'donors': User.query.filter_by(role='donor').count(),
            'receivers': User.query.filter_by(role='receiver').count(),
            'total_listings': FoodListing.query.count(),
            'active_listings': FoodListing.query.filter_by(status='available').count(),
            'total_claims': Claim.query.count()
        }
    })

@app.route('/api/predict')
def api_predict():
    """ML model returns surplus prediction"""
    from ml.predict import get_predictions
    predictions = get_predictions()
    return jsonify({'success': True, 'predictions': predictions})

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Save contact form message"""
    data = request.get_json()

    message = ContactMessage(
        name=data['name'],
        email=data['email'],
        message=data['message']
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Message sent successfully'})

@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload_image():
    """Upload food image"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        return jsonify({
            'success': True,
            'message': 'File uploaded',
            'path': f'/static/uploads/{filename}'
        })

    return jsonify({'success': False, 'message': 'Invalid file type'}), 400

@app.route('/api/admin/approve-user/<int:id>', methods=['POST'])
@login_required
def api_approve_user(id):
    """Admin approves user"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    user = User.query.get_or_404(id)
    user.is_verified = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'User approved'})

@app.route('/api/admin/delete-user/<int:id>', methods=['POST'])
@login_required
def api_delete_user(id):
    """Admin deletes user"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'User deleted'})

# Import datetime for use in routes
from datetime import datetime

# ============ CREATE DATABASE ============

with app.app_context():
    db.create_all()

    # Train ML model if not exists
    import os
    ml_model_path = os.path.join(os.path.dirname(__file__), 'ml', 'model.pkl')
    if not os.path.exists(ml_model_path):
        print("Training ML model for first run...")
        try:
            import subprocess
            result = subprocess.run(['python', 'ml/model.py'], capture_output=True, text=True)
            if result.returncode == 0:
                print("ML model trained successfully!")
            else:
                print(f"ML training warning: {result.stderr}")
        except Exception as e:
            print(f"ML training error (non-critical): {e}")

    # Create admin user if not exists
    admin = User.query.filter_by(email='admin@foodbridge.org').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@foodbridge.org',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            zone='Zone A'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@foodbridge.org / admin123")

    # ============ SEED DATA ============
    # Only add sample data if database is empty
    if User.query.filter_by(role='donor').count() == 0:
        print("Seeding database with sample data...")

        from datetime import timedelta

        # Create sample donors
        donors = [
            User(name='Green Bistro', email='green@bistro.com', password_hash=generate_password_hash('donor123'), role='donor', phone='+1-555-0101', address='123 Main St, Downtown', zone='Zone A', is_verified=True),
            User(name='Fresh Mart', email='fresh@mart.com', password_hash=generate_password_hash('donor123'), role='donor', phone='+1-555-0102', address='456 Oak Ave, North District', zone='Zone B', is_verified=True),
            User(name='Sunrise Bakery', email='sunrise@bakery.com', password_hash=generate_password_hash('donor123'), role='donor', phone='+1-555-0103', address='789 Elm St, South District', zone='Zone C', is_verified=True),
            User(name='Harvest Kitchen', email='harvest@kitchen.com', password_hash=generate_password_hash('donor123'), role='donor', phone='+1-555-0104', address='321 Pine Rd, East District', zone='Zone D', is_verified=True),
            User(name='Community Diner', email='community@diner.com', password_hash=generate_password_hash('donor123'), role='donor', phone='+1-555-0105', address='654 Cedar Ln, Downtown', zone='Zone A', is_verified=True),
        ]
        for d in donors:
            db.session.add(d)
        db.session.commit()

        # Create sample receiver
        receiver = User(
            name='Hope Orphanage', email='hope@orphanage.org',
            password_hash=generate_password_hash('receiver123'),
            role='receiver', phone='+1-555-0201',
            address='111 Charity Blvd', zone='Zone A',
            registration_number='NGO-2024-001', is_verified=True
        )
        db.session.add(receiver)
        db.session.commit()

        # Create sample food listings across all zones and categories
        now = datetime.utcnow()
        listings = [
            # Zone A - Cooked
            FoodListing(donor_id=donors[0].id, food_name='Vegetable Biryani', quantity=8.0, category='Cooked', expiry_time=now + timedelta(hours=6), pickup_address='123 Main St, Downtown', zone='Zone A', description='Fresh vegetable biryani made today. Serves 30+ people.', status='available'),
            FoodListing(donor_id=donors[4].id, food_name='Chicken Curry', quantity=5.0, category='Cooked', expiry_time=now + timedelta(hours=4), pickup_address='654 Cedar Ln, Downtown', zone='Zone A', description='Homemade chicken curry with rice. Still hot!', status='available'),
            # Zone A - Raw
            FoodListing(donor_id=donors[0].id, food_name='Fresh Tomatoes', quantity=12.0, category='Raw', expiry_time=now + timedelta(hours=48), pickup_address='123 Main St, Downtown', zone='Zone A', description='Farm-fresh tomatoes, slightly overripe but perfect for cooking.', status='available'),
            # Zone A - Packaged
            FoodListing(donor_id=donors[4].id, food_name='Canned Beans', quantity=6.0, category='Packaged', expiry_time=now + timedelta(days=30), pickup_address='654 Cedar Ln, Downtown', zone='Zone A', description='Assorted canned beans - kidney, black, and pinto.', status='available'),
            # Zone B - Cooked
            FoodListing(donor_id=donors[1].id, food_name='Dal Makhani', quantity=10.0, category='Cooked', expiry_time=now + timedelta(hours=5), pickup_address='456 Oak Ave, North District', zone='Zone B', description='Rich dal makhani with naan bread. Enough for 40 people.', status='available'),
            # Zone B - Raw
            FoodListing(donor_id=donors[1].id, food_name='Organic Carrots', quantity=15.0, category='Raw', expiry_time=now + timedelta(hours=72), pickup_address='456 Oak Ave, North District', zone='Zone B', description='Bulk organic carrots from local farm. Great condition.', status='available'),
            FoodListing(donor_id=donors[1].id, food_name='Mixed Vegetables', quantity=8.0, category='Raw', expiry_time=now + timedelta(hours=36), pickup_address='456 Oak Ave, North District', zone='Zone B', description='Peppers, onions, zucchini mix. Slightly bruised.', status='available'),
            # Zone B - Packaged
            FoodListing(donor_id=donors[1].id, food_name='Rice Bags (5kg each)', quantity=20.0, category='Packaged', expiry_time=now + timedelta(days=90), pickup_address='456 Oak Ave, North District', zone='Zone B', description='Four 5kg bags of basmati rice. Unopened.', status='available'),
            # Zone C - Cooked
            FoodListing(donor_id=donors[2].id, food_name='Bread Loaves', quantity=7.0, category='Cooked', expiry_time=now + timedelta(hours=12), pickup_address='789 Elm St, South District', zone='Zone C', description='Freshly baked whole wheat bread. 14 loaves available.', status='available'),
            FoodListing(donor_id=donors[2].id, food_name='Pasta Alfredo', quantity=4.0, category='Cooked', expiry_time=now + timedelta(hours=3), pickup_address='789 Elm St, South District', zone='Zone C', description='Creamy pasta alfredo. Needs pickup ASAP.', status='available'),
            # Zone C - Raw
            FoodListing(donor_id=donors[2].id, food_name='Apples', quantity=10.0, category='Raw', expiry_time=now + timedelta(hours=48), pickup_address='789 Elm St, South District', zone='Zone C', description='Fresh red apples from orchard surplus.', status='available'),
            # Zone D - Cooked
            FoodListing(donor_id=donors[3].id, food_name='Fish Stew', quantity=6.0, category='Cooked', expiry_time=now + timedelta(hours=4), pickup_address='321 Pine Rd, East District', zone='Zone D', description='Hearty fish stew with vegetables. Serves 24.', status='available'),
            FoodListing(donor_id=donors[3].id, food_name='Mutton Biryani', quantity=12.0, category='Cooked', expiry_time=now + timedelta(hours=5), pickup_address='321 Pine Rd, East District', zone='Zone D', description='Catering leftover mutton biryani from event. Excellent quality.', status='available'),
            # Zone D - Raw
            FoodListing(donor_id=donors[3].id, food_name='Potatoes', quantity=20.0, category='Raw', expiry_time=now + timedelta(days=14), pickup_address='321 Pine Rd, East District', zone='Zone D', description='Large sack of potatoes. Perfect for community kitchens.', status='available'),
            FoodListing(donor_id=donors[3].id, food_name='Onions', quantity=10.0, category='Raw', expiry_time=now + timedelta(days=10), pickup_address='321 Pine Rd, East District', zone='Zone D', description='Fresh onions, bulk quantity.', status='available'),
            # Zone D - Packaged
            FoodListing(donor_id=donors[3].id, food_name='Cereal Boxes', quantity=8.0, category='Packaged', expiry_time=now + timedelta(days=60), pickup_address='321 Pine Rd, East District', zone='Zone D', description='Assorted breakfast cereals. Sealed and unexpired.', status='available'),
            # Already claimed listing (to show variety)
            FoodListing(donor_id=donors[0].id, food_name='Samosas (100 pcs)', quantity=5.0, category='Cooked', expiry_time=now + timedelta(hours=2), pickup_address='123 Main St, Downtown', zone='Zone A', description='Party leftover samosas. Still crispy!', status='claimed'),
        ]

        for l in listings:
            db.session.add(l)

        # Create ML training records
        import random
        zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        categories = ['Cooked', 'Raw', 'Packaged']

        for _ in range(200):
            record = DonationRecord(
                zone=random.choice(zones),
                day_of_week=random.choice(days),
                hour=random.randint(8, 22),
                quantity=round(random.gauss(15, 5), 2),
                category=random.choice(categories),
                month=random.randint(1, 12)
            )
            db.session.add(record)

        db.session.commit()
        print("Sample data seeded successfully!")
        print("  Donors: 5 accounts (password: donor123)")
        print("  Receiver: hope@orphanage.org (password: receiver123)")
        print("  Food listings: 17 items across all zones and categories")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
