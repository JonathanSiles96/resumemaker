"""
Payment model for tracking payment transactions
"""
from datetime import datetime
from .database import db

class Payment(db.Model):
    """Payment model - tracks all payment transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Payment details
    amount = db.Column(db.Float, nullable=False)  # Amount in USD
    currency = db.Column(db.String(10), default='USD', nullable=False)
    
    # Provider info
    provider = db.Column(db.String(50), nullable=False)  # 'stripe', 'paypal', 'coingate'
    provider_payment_id = db.Column(db.String(255), nullable=True)  # External payment ID
    provider_order_id = db.Column(db.String(255), nullable=True)  # External order ID
    
    # Status
    status = db.Column(db.String(50), default='pending', nullable=False)
    # Statuses: pending, processing, completed, failed, refunded
    
    # Crypto-specific fields
    crypto_currency = db.Column(db.String(20), nullable=True)  # e.g., 'USDT'
    crypto_network = db.Column(db.String(20), nullable=True)  # e.g., 'TRC20', 'ERC20', 'BEP20'
    crypto_amount = db.Column(db.String(50), nullable=True)
    crypto_address = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.provider} - {self.status}>'
    
    def mark_completed(self):
        """Mark payment as completed and activate user"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        # Mark user as paid
        self.user.mark_paid()
        db.session.commit()
    
    def mark_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'amount': self.amount,
            'currency': self.currency,
            'provider': self.provider,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def create_payment(cls, user_id, amount, provider, **kwargs):
        """Create a new payment record"""
        payment = cls(
            user_id=user_id,
            amount=amount,
            provider=provider,
            **kwargs
        )
        db.session.add(payment)
        db.session.commit()
        return payment
    
    @classmethod
    def get_by_provider_id(cls, provider, provider_payment_id):
        """Get payment by provider's payment ID"""
        return cls.query.filter_by(
            provider=provider,
            provider_payment_id=provider_payment_id
        ).first()
    
    @classmethod
    def get_by_provider_order_id(cls, provider, provider_order_id):
        """Get payment by provider's order ID"""
        return cls.query.filter_by(
            provider=provider,
            provider_order_id=provider_order_id
        ).first()

