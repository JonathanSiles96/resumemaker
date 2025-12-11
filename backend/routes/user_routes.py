"""
User API Routes
Handles user registration, status checking, and authentication
"""
from flask import Blueprint, request, jsonify
from models import db, User

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/register', methods=['POST'])
def register_user():
    """
    Register or identify a user by email
    Creates new user if doesn't exist
    """
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Get or create user
        user = User.get_or_create(email)
        
        return jsonify({
            'success': True,
            'user': user.get_status()
        })
        
    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/status', methods=['POST'])
def get_user_status():
    """
    Get user status by email
    Returns payment status, usage, and whether they can generate
    """
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        user = User.get_by_email(email)
        
        if not user:
            return jsonify({
                'success': True,
                'user': {
                    'email': email,
                    'is_paid': False,
                    'free_used': False,
                    'can_generate': True,
                    'total_generations': 0,
                    'needs_payment': False,
                    'exists': False
                }
            })
        
        status = user.get_status()
        status['exists'] = True
        
        return jsonify({
            'success': True,
            'user': status
        })
        
    except Exception as e:
        print(f"Error getting user status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@user_bp.route('/check-access', methods=['POST'])
def check_access():
    """
    Check if user can generate a resume
    Used before generation to verify access
    """
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'can_generate': False,
                'error': 'Email is required'
            }), 400
        
        user = User.get_by_email(email)
        
        if not user:
            # New user - can use free generation
            return jsonify({
                'success': True,
                'can_generate': True,
                'is_paid': False,
                'is_free': True,
                'message': 'First generation is free!'
            })
        
        if user.is_paid:
            return jsonify({
                'success': True,
                'can_generate': True,
                'is_paid': True,
                'is_free': False,
                'message': 'Lifetime access active'
            })
        
        if not user.free_used:
            return jsonify({
                'success': True,
                'can_generate': True,
                'is_paid': False,
                'is_free': True,
                'message': 'First generation is free!'
            })
        
        # User has used free generation and hasn't paid
        return jsonify({
            'success': True,
            'can_generate': False,
            'is_paid': False,
            'is_free': False,
            'needs_payment': True,
            'message': 'Payment required for unlimited access'
        })
        
    except Exception as e:
        print(f"Error checking access: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

