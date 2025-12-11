"""
User model for tracking users and their payment status
"""
from datetime import datetime
from .database import db

class User(db.Model):
    """User model - tracks email, payment status, and usage"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Payment status
    is_paid = db.Column(db.Boolean, default=False, nullable=False)
    
    # Usage tracking
    free_generations_used = db.Column(db.Integer, default=0, nullable=False)  # Track number of free generations used
    total_generations = db.Column(db.Integer, default=0, nullable=False)
    
    # Free tier limit
    FREE_GENERATION_LIMIT = 3  # Users get 3 free tries
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    payments = db.relationship('Payment', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def can_generate(self):
        """Check if user can generate a resume"""
        # Paid users can always generate
        if self.is_paid:
            return True
        # Free users can generate up to FREE_GENERATION_LIMIT times
        if self.free_generations_used < self.FREE_GENERATION_LIMIT:
            return True
        return False
    
    def get_remaining_free_tries(self):
        """Get number of remaining free generations"""
        if self.is_paid:
            return -1  # Unlimited for paid users
        return max(0, self.FREE_GENERATION_LIMIT - self.free_generations_used)
    
    def get_status(self):
        """Get user status for API response"""
        return {
            'email': self.email,
            'is_paid': self.is_paid,
            'free_generations_used': self.free_generations_used,
            'free_generations_remaining': self.get_remaining_free_tries(),
            'can_generate': self.can_generate(),
            'total_generations': self.total_generations,
            'needs_payment': self.free_generations_used >= self.FREE_GENERATION_LIMIT and not self.is_paid
        }
    
    def mark_free_used(self):
        """Mark that the user has used one of their free generations"""
        self.free_generations_used += 1
        self.total_generations += 1
        db.session.commit()
    
    def mark_paid(self):
        """Mark user as paid (lifetime access)"""
        self.is_paid = True
        self.paid_at = datetime.utcnow()
        db.session.commit()
    
    def increment_generations(self):
        """Increment the generation count"""
        self.total_generations += 1
        db.session.commit()
    
    @classmethod
    def get_or_create(cls, email):
        """Get existing user or create new one"""
        email = email.lower().strip()
        user = cls.query.filter_by(email=email).first()
        if not user:
            user = cls(email=email)
            db.session.add(user)
            db.session.commit()
        return user
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email.lower().strip()).first()

