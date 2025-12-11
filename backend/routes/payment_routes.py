"""
Payment API Routes
Handles payment creation, webhooks, and verification
"""
from flask import Blueprint, request, jsonify, current_app
from models import db, User, Payment
from services.payment import StripeService, PayPalService, CoinGateService
import os
import uuid

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Initialize payment services
stripe_service = StripeService()
paypal_service = PayPalService()
coingate_service = CoinGateService()

# Price constant
PRICE_USD = 25.00


@payment_bp.route('/config', methods=['GET'])
def get_payment_config():
    """Get payment configuration for frontend"""
    return jsonify({
        'success': True,
        'price': PRICE_USD,
        'currency': 'USD',
        'providers': {
            'stripe': {
                'enabled': stripe_service.is_configured(),
                'public_key': os.getenv('STRIPE_PUBLIC_KEY', '')
            },
            'paypal': {
                'enabled': paypal_service.is_configured(),
                'client_id': os.getenv('PAYPAL_CLIENT_ID', ''),
                'mode': os.getenv('PAYPAL_MODE', 'sandbox')
            },
            'coingate': {
                'enabled': coingate_service.is_configured(),
                'currencies': ['USDT (TRC20)', 'USDT (ERC20)', 'USDT (BEP20)', 'BTC', 'ETH']
            }
        }
    })


# ============== STRIPE ==============

@payment_bp.route('/stripe/create-session', methods=['POST'])
def create_stripe_session():
    """Create Stripe checkout session"""
    try:
        if not stripe_service.is_configured():
            return jsonify({'success': False, 'error': 'Stripe is not configured'}), 503
        
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Get or create user
        user = User.get_or_create(email)
        
        # Check if already paid
        if user.is_paid:
            return jsonify({
                'success': False,
                'error': 'You already have lifetime access!'
            }), 400
        
        # Get base URL for redirects
        base_url = os.getenv('APP_URL', request.host_url.rstrip('/'))
        
        # Create Stripe session
        session = stripe_service.create_checkout_session(
            user_email=email,
            success_url=f"{base_url}/payment-success",
            cancel_url=f"{base_url}/payment-cancelled"
        )
        
        # Create payment record
        payment = Payment.create_payment(
            user_id=user.id,
            amount=PRICE_USD,
            provider='stripe',
            provider_payment_id=session['session_id'],
            status='pending'
        )
        
        return jsonify({
            'success': True,
            'session_id': session['session_id'],
            'checkout_url': session['checkout_url'],
            'public_key': session['public_key']
        })
        
    except Exception as e:
        print(f"Stripe session error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')
        
        event = stripe_service.verify_webhook(payload, signature)
        if not event:
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            session_id = session['id']
            customer_email = session.get('customer_email') or session.get('metadata', {}).get('user_email')
            
            print(f"✓ Stripe payment completed for {customer_email}")
            
            # Find and update payment
            payment = Payment.get_by_provider_id('stripe', session_id)
            if payment:
                payment.mark_completed()
                print(f"✓ User {customer_email} activated with lifetime access")
            else:
                # Create payment if not found (edge case)
                user = User.get_or_create(customer_email)
                payment = Payment.create_payment(
                    user_id=user.id,
                    amount=PRICE_USD,
                    provider='stripe',
                    provider_payment_id=session_id,
                    status='completed'
                )
                user.mark_paid()
        
        return jsonify({'received': True})
        
    except Exception as e:
        print(f"Stripe webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/stripe/verify', methods=['POST'])
def verify_stripe_payment():
    """Verify Stripe payment after redirect"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        session = stripe_service.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        if session['payment_status'] == 'paid':
            # Ensure user is marked as paid
            email = session['customer_email'] or session.get('metadata', {}).get('user_email')
            if email:
                user = User.get_by_email(email)
                if user and not user.is_paid:
                    user.mark_paid()
            
            return jsonify({
                'success': True,
                'paid': True,
                'email': email
            })
        
        return jsonify({
            'success': True,
            'paid': False,
            'status': session['payment_status']
        })
        
    except Exception as e:
        print(f"Stripe verify error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== PAYPAL ==============

@payment_bp.route('/paypal/create-order', methods=['POST'])
def create_paypal_order():
    """Create PayPal order"""
    try:
        if not paypal_service.is_configured():
            return jsonify({'success': False, 'error': 'PayPal is not configured'}), 503
        
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Get or create user
        user = User.get_or_create(email)
        
        # Check if already paid
        if user.is_paid:
            return jsonify({
                'success': False,
                'error': 'You already have lifetime access!'
            }), 400
        
        # Get base URL for redirects
        base_url = os.getenv('APP_URL', request.host_url.rstrip('/'))
        
        # Create PayPal order
        order = paypal_service.create_order(
            user_email=email,
            return_url=f"{base_url}/payment-success?provider=paypal",
            cancel_url=f"{base_url}/payment-cancelled"
        )
        
        # Create payment record
        payment = Payment.create_payment(
            user_id=user.id,
            amount=PRICE_USD,
            provider='paypal',
            provider_order_id=order['order_id'],
            status='pending'
        )
        
        return jsonify({
            'success': True,
            'order_id': order['order_id'],
            'approval_url': order['approval_url']
        })
        
    except Exception as e:
        print(f"PayPal order error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/paypal/capture-order', methods=['POST'])
def capture_paypal_order():
    """Capture (complete) PayPal order after approval"""
    try:
        data = request.json
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({'success': False, 'error': 'Order ID required'}), 400
        
        # Capture the order
        capture = paypal_service.capture_order(order_id)
        
        if capture and capture['status'] == 'COMPLETED':
            # Find and update payment
            payment = Payment.get_by_provider_order_id('paypal', order_id)
            if payment:
                payment.mark_completed()
                email = payment.user.email
            else:
                # Get email from capture
                email = capture.get('custom_id') or capture.get('payer_email')
                if email:
                    user = User.get_or_create(email)
                    payment = Payment.create_payment(
                        user_id=user.id,
                        amount=PRICE_USD,
                        provider='paypal',
                        provider_order_id=order_id,
                        status='completed'
                    )
                    user.mark_paid()
            
            print(f"✓ PayPal payment completed for {email}")
            
            return jsonify({
                'success': True,
                'paid': True,
                'email': email
            })
        
        return jsonify({
            'success': False,
            'error': 'Payment capture failed'
        }), 400
        
    except Exception as e:
        print(f"PayPal capture error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== COINGATE (CRYPTO) ==============

@payment_bp.route('/coingate/create-order', methods=['POST'])
def create_coingate_order():
    """Create CoinGate crypto payment order"""
    try:
        if not coingate_service.is_configured():
            return jsonify({'success': False, 'error': 'Crypto payments are not configured'}), 503
        
        data = request.json
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Get or create user
        user = User.get_or_create(email)
        
        # Check if already paid
        if user.is_paid:
            return jsonify({
                'success': False,
                'error': 'You already have lifetime access!'
            }), 400
        
        # Generate unique order ID
        internal_order_id = f"RM-{user.id}-{uuid.uuid4().hex[:8]}"
        
        # Get base URL
        base_url = os.getenv('APP_URL', request.host_url.rstrip('/'))
        
        # Create CoinGate order
        order = coingate_service.create_order(
            user_email=email,
            order_id=internal_order_id,
            success_url=f"{base_url}/payment-success?provider=coingate",
            cancel_url=f"{base_url}/payment-cancelled",
            callback_url=f"{base_url}/api/payment/coingate/webhook"
        )
        
        # Create payment record
        payment = Payment.create_payment(
            user_id=user.id,
            amount=PRICE_USD,
            provider='coingate',
            provider_payment_id=str(order['coingate_id']),
            provider_order_id=internal_order_id,
            status='pending'
        )
        
        return jsonify({
            'success': True,
            'payment_url': order['payment_url'],
            'order_id': internal_order_id,
            'coingate_id': order['coingate_id']
        })
        
    except Exception as e:
        print(f"CoinGate order error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/coingate/webhook', methods=['POST'])
def coingate_webhook():
    """Handle CoinGate webhook callbacks"""
    try:
        # CoinGate sends form data
        data = request.form.to_dict() if request.form else request.json
        
        print(f"CoinGate webhook received: {data}")
        
        if not coingate_service.verify_callback(data):
            return jsonify({'error': 'Invalid callback'}), 400
        
        coingate_id = str(data.get('id'))
        order_id = data.get('order_id')
        status = data.get('status')
        
        # Find payment
        payment = Payment.get_by_provider_id('coingate', coingate_id)
        if not payment:
            payment = Payment.get_by_provider_order_id('coingate', order_id)
        
        if not payment:
            print(f"Payment not found for CoinGate order: {coingate_id} / {order_id}")
            return jsonify({'error': 'Payment not found'}), 404
        
        # Update based on status
        if coingate_service.is_payment_successful(status):
            payment.status = 'completed'
            payment.crypto_currency = data.get('pay_currency')
            payment.crypto_amount = data.get('pay_amount')
            payment.mark_completed()
            print(f"✓ CoinGate payment completed for user {payment.user.email}")
        elif status in ['expired', 'canceled', 'invalid']:
            payment.mark_failed()
            print(f"✗ CoinGate payment failed: {status}")
        else:
            # Update status for pending/confirming
            payment.status = status
            db.session.commit()
        
        return jsonify({'received': True})
        
    except Exception as e:
        print(f"CoinGate webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/coingate/check', methods=['POST'])
def check_coingate_payment():
    """Check CoinGate payment status"""
    try:
        data = request.json
        coingate_id = data.get('coingate_id')
        order_id = data.get('order_id')
        
        if coingate_id:
            order = coingate_service.get_order(coingate_id)
            if order:
                status = order.get('status')
                if coingate_service.is_payment_successful(status):
                    # Update payment if needed
                    payment = Payment.get_by_provider_id('coingate', str(coingate_id))
                    if payment and payment.status != 'completed':
                        payment.mark_completed()
                    
                    return jsonify({
                        'success': True,
                        'paid': True,
                        'status': status
                    })
                
                return jsonify({
                    'success': True,
                    'paid': False,
                    'status': status
                })
        
        return jsonify({
            'success': False,
            'error': 'Order not found'
        }), 404
        
    except Exception as e:
        print(f"CoinGate check error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

