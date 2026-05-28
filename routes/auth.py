"""
Authentication Routes
"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    # Validate required fields
    if not all(k in data for k in ['name', 'email', 'password', 'role']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

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

    return jsonify({'success': True, 'message': 'Registration successful'}), 201


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()

    user = User.query.filter_by(email=data.get('email')).first()

    if user and check_password_hash(user.password_hash, data.get('password', '')):
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        })

    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401


@auth_bp.route('/auth/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})
