"""
Admin Routes
"""

from flask import Blueprint, request, jsonify, make_response
from flask_login import login_required, current_user
from models import db, User, FoodListing, Claim, ContactMessage
from datetime import datetime
import csv
import io

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/users')
@login_required
@admin_required
def get_all_users():
    """Admin gets all users"""
    users = User.query.order_by(User.created_at.desc()).all()

    return jsonify({
        'success': True,
        'users': [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'phone': u.phone,
            'address': u.address,
            'zone': u.zone,
            'is_verified': u.is_verified,
            'created_at': u.created_at.isoformat()
        } for u in users]
    })


@admin_bp.route('/users/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(id):
    """Admin approves a user"""
    user = User.query.get_or_404(id)
    user.is_verified = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'User approved'})


@admin_bp.route('/users/<int:id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(id):
    """Admin rejects/deletes a user"""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'User rejected and deleted'})


@admin_bp.route('/listings')
@login_required
@admin_required
def get_all_listings():
    """Admin gets all listings"""
    listings = FoodListing.query.order_by(FoodListing.created_at.desc()).all()

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
            'status': l.status,
            'donor_id': l.donor_id,
            'donor_name': l.donor.name,
            'created_at': l.created_at.isoformat()
        } for l in listings]
    })


@admin_bp.route('/claims')
@login_required
@admin_required
def get_all_claims():
    """Admin gets all claims"""
    claims = Claim.query.order_by(Claim.claimed_at.desc()).all()

    return jsonify({
        'success': True,
        'claims': [{
            'id': c.id,
            'listing_id': c.listing_id,
            'listing_name': c.listing.food_name,
            'receiver_id': c.receiver_id,
            'receiver_name': c.receiver.name,
            'status': c.status,
            'claimed_at': c.claimed_at.isoformat()
        } for c in claims]
    })


@admin_bp.route('/stats')
@login_required
@admin_required
def get_stats():
    """Admin gets platform stats"""
    return jsonify({
        'success': True,
        'stats': {
            'total_users': User.query.count(),
            'donors': User.query.filter_by(role='donor').count(),
            'receivers': User.query.filter_by(role='receiver').count(),
            'total_listings': FoodListing.query.count(),
            'available_listings': FoodListing.query.filter_by(status='available').count(),
            'claimed_listings': FoodListing.query.filter_by(status='claimed').count(),
            'completed_listings': FoodListing.query.filter_by(status='completed').count(),
            'total_claims': Claim.query.count(),
            'pending_claims': Claim.query.filter_by(status='pending').count()
        }
    })


@admin_bp.route('/export/users')
@login_required
@admin_required
def export_users_csv():
    """Export users as CSV"""
    users = User.query.order_by(User.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['ID', 'Name', 'Email', 'Role', 'Phone', 'Address', 'Zone', 'Verified', 'Created At'])

    for u in users:
        writer.writerow([
            u.id, u.name, u.email, u.role, u.phone, u.address, u.zone,
            'Yes' if u.is_verified else 'No', u.created_at.isoformat()
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=users.csv'
    response.headers['Content-type'] = 'text/csv'

    return response


@admin_bp.route('/export/listings')
@login_required
@admin_required
def export_listings_csv():
    """Export listings as CSV"""
    listings = FoodListing.query.order_by(FoodListing.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['ID', 'Food Name', 'Quantity (kg)', 'Category', 'Expiry', 'Zone', 'Status', 'Donor', 'Created At'])

    for l in listings:
        writer.writerow([
            l.id, l.food_name, l.quantity, l.category, l.expiry_time.isoformat(),
            l.zone, l.status, l.donor.name, l.created_at.isoformat()
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=listings.csv'
    response.headers['Content-type'] = 'text/csv'

    return response


@admin_bp.route('/contact-messages')
@login_required
@admin_required
def get_contact_messages():
    """Admin gets all contact messages"""
    messages = ContactMessage.query.order_by(ContactMessage.sent_at.desc()).all()

    return jsonify({
        'success': True,
        'messages': [{
            'id': m.id,
            'name': m.name,
            'email': m.email,
            'message': m.message,
            'sent_at': m.sent_at.isoformat()
        } for m in messages]
    })
