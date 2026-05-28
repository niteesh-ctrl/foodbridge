"""
FoodBridge Database Models
SQLAlchemy ORM Models
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for donors, receivers, and admins"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='donor')  # donor, receiver, admin
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    zone = db.Column(db.String(20), default='Zone A')  # Zone A, B, C, D
    registration_number = db.Column(db.String(50))  # For receivers (NGOs, orphanages)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    donations = db.relationship('FoodListing', backref='donor', lazy=True)
    claims = db.relationship('Claim', backref='receiver', lazy=True)

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'


class FoodListing(db.Model):
    """Food listing model for donations"""
    __tablename__ = 'food_listings'

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # in kg
    category = db.Column(db.String(30), nullable=False)  # Cooked, Raw, Packaged
    expiry_time = db.Column(db.DateTime, nullable=False)
    pickup_address = db.Column(db.String(200), nullable=False)
    zone = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='available')  # available, claimed, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    claims = db.relationship('Claim', backref='listing', lazy=True)

    def __repr__(self):
        return f'<FoodListing {self.food_name} ({self.status})>'


class Claim(db.Model):
    """Claim model for receivers claiming food listings"""
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('food_listings.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Claim {self.id} - Listing {self.listing_id}>'


class ContactMessage(db.Model):
    """Contact form messages"""
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage from {self.name}>'


class DonationRecord(db.Model):
    """Donation records for ML training"""
    __tablename__ = 'donation_records'

    id = db.Column(db.Integer, primary_key=True)
    zone = db.Column(db.String(20), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)  # Monday, Tuesday, etc.
    hour = db.Column(db.Integer, nullable=False)  # 0-23
    quantity = db.Column(db.Float, nullable=False)  # in kg
    category = db.Column(db.String(30), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DonationRecord {self.zone} - {self.day_of_week}>'
