"""
Database initialization and configuration
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumemaker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Import models to ensure they're registered
        from . import User, Payment
        # Create all tables
        db.create_all()
        print("✓ Database initialized")
    
    return db

