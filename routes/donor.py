"""
Donor Routes
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, FoodListing, DonationRecord
from datetime import datetime
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

donor_bp = Blueprint('donor', __name__)

@donor_bp.route('/listings', methods=['POST'])
@login_required
def create_listing():
    """Donor posts new food listing"""
    if current_user.role != 'donor':
        return jsonify({'success': False, 'message': 'Only donors can post listings'}), 403

    data = request.get_json()

    # Handle file upload if provided
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_path = f'/static/uploads/{filename}'

    listing = FoodListing(
        donor_id=current_user.id,
        food_name=data['food_name'],
        quantity=float(data['quantity']),
        category=data['category'],
        expiry_time=datetime.fromisoformat(data['expiry_time']),
        pickup_address=data['pickup_address'],
        zone=data['zone'],
        description=data.get('description', ''),
        image_path=image_path or data.get('image_path')
    )

    # Record for ML training
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

    return jsonify({'success': True, 'message': 'Listing created', 'id': listing.id}), 201


@donor_bp.route('/listings/<int:id>', methods=['PUT'])
@login_required
def update_listing(id):
    """Donor edits listing"""
    listing = FoodListing.query.get_or_404(id)

    if listing.donor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()

    listing.food_name = data.get('food_name', listing.food_name)
    listing.quantity = float(data.get('quantity', listing.quantity))
    listing.category = data.get('category', listing.category)

    if 'expiry_time' in data:
        listing.expiry_time = datetime.fromisoformat(data['expiry_time'])

    listing.pickup_address = data.get('pickup_address', listing.pickup_address)
    listing.zone = data.get('zone', listing.zone)
    listing.description = data.get('description', listing.description)

    if 'image_path' in data:
        listing.image_path = data['image_path']

    db.session.commit()

    return jsonify({'success': True, 'message': 'Listing updated'})


@donor_bp.route('/listings/<int:id>', methods=['DELETE'])
@login_required
def delete_listing(id):
    """Donor deletes listing"""
    listing = FoodListing.query.get_or_404(id)

    if listing.donor_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    db.session.delete(listing)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Listing deleted'})


@donor_bp.route('/donor/listings')
@login_required
def get_my_listings():
    """Get donor's own listings"""
    if current_user.role != 'donor':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    listings = FoodListing.query.filter_by(donor_id=current_user.id).order_by(
        FoodListing.created_at.desc()
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
            'status': l.status,
            'created_at': l.created_at.isoformat()
        } for l in listings]
    })
