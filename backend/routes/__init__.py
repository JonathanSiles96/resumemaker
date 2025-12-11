"""
API Routes for Resume Maker
"""
from .payment_routes import payment_bp
from .user_routes import user_bp
from .analytics_routes import analytics_bp

__all__ = ['payment_bp', 'user_bp', 'analytics_bp']

