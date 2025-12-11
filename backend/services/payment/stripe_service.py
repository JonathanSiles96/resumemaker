"""
Stripe Payment Service
Handles Stripe checkout sessions and webhooks
"""
import stripe
import os
from typing import Optional, Dict, Any

class StripeService:
    """Stripe payment integration"""
    
    PRICE_USD = 25.00  # Lifetime access price
    
    def __init__(self):
        self.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        self.public_key = os.getenv('STRIPE_PUBLIC_KEY')
        
        if self.api_key:
            stripe.api_key = self.api_key
            print("✓ Stripe initialized")
        else:
            print("⚠ Stripe API key not configured")
    
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(self.api_key)
    
    def create_checkout_session(self, user_email: str, success_url: str, cancel_url: str) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe Checkout Session for one-time payment
        
        Args:
            user_email: Customer's email
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            
        Returns:
            Dict with session_id and checkout_url, or None on error
        """
        if not self.is_configured():
            raise Exception("Stripe is not configured")
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Resume Maker - Lifetime Access',
                            'description': 'Unlimited AI-powered resume generation forever',
                        },
                        'unit_amount': int(self.PRICE_USD * 100),  # Stripe uses cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={
                    'user_email': user_email,
                    'product': 'lifetime_access'
                }
            )
            
            return {
                'session_id': session.id,
                'checkout_url': session.url,
                'public_key': self.public_key
            }
            
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise Exception(f"Payment error: {str(e)}")
    
    def verify_webhook(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """
        Verify and parse Stripe webhook
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header
            
        Returns:
            Parsed event data or None
        """
        if not self.webhook_secret:
            print("⚠ Stripe webhook secret not configured")
            return None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            print(f"Webhook signature verification failed: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get checkout session details"""
        if not self.is_configured():
            return None
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'id': session.id,
                'payment_status': session.payment_status,
                'customer_email': session.customer_email,
                'amount_total': session.amount_total / 100,  # Convert from cents
                'metadata': session.metadata
            }
        except stripe.error.StripeError as e:
            print(f"Error retrieving session: {e}")
            return None

