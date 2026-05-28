"""
Receiver Routes
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, FoodListing, Claim
from datetime import datetime

receiver_bp = Blueprint('receiver', __name__)

@receiver_bp.route('/claim/<int:id>', methods=['POST'])
@login_required
def claim_listing(id):
    """Receiver claims a listing"""
    if current_user.role != 'receiver':
        return jsonify({'success': False, 'message': 'Only receivers can claim listings'}), 403

    listing = FoodListing.query.get_or_404(id)

    if listing.status != 'available':
        return jsonify({'success': False, 'message': 'Listing no longer available'}), 400

    # Check if listing is expired
    if listing.expiry_time < datetime.utcnow():
        listing.status = 'expired'
        db.session.commit()
        return jsonify({'success': False, 'message': 'Listing has expired'}), 400

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
    }), 201


@receiver_bp.route('/claims')
@login_required
def get_my_claims():
    """Get receiver's claims"""
    if current_user.role != 'receiver':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    claims = Claim.query.filter_by(receiver_id=current_user.id).order_by(
        Claim.claimed_at.desc()
    ).all()

    return jsonify({
        'success': True,
        'claims': [{
            'id': c.id,
            'listing': {
                'id': c.listing.id,
                'food_name': c.listing.food_name,
                'quantity': c.listing.quantity,
                'category': c.listing.category,
                'pickup_address': c.listing.pickup_address,
                'zone': c.listing.zone,
                'image_path': c.listing.image_path
            },
            'donor': {
                'name': c.listing.donor.name,
                'phone': c.listing.donor.phone
            },
            'status': c.status,
            'claimed_at': c.claimed_at.isoformat()
        } for c in claims]
    })


@receiver_bp.route('/claims/<int:id>', methods=['PUT'])
@login_required
def update_claim_status(id):
    """Update claim status"""
    claim = Claim.query.get_or_404(id)

    if claim.receiver_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    claim.status = data.get('status', claim.status)

    if claim.status == 'completed':
        claim.listing.status = 'completed'

    db.session.commit()

    return jsonify({'success': True, 'message': 'Claim status updated'})


@receiver_bp.route('/listings')
def get_available_listings():
    """Get all available listings with filters"""
    query = FoodListing.query.filter_by(status='available')

    # Filter by zone
    zone = request.args.get('zone')
    if zone:
        query = query.filter_by(zone=zone)

    # Filter by category
    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)

    # Filter by min quantity
    min_quantity = request.args.get('min_quantity')
    if min_quantity:
        query = query.filter(FoodListing.quantity >= float(min_quantity))

    listings = query.order_by(FoodListing.expiry_time.asc()).all()

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
