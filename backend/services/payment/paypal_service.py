"""
PayPal Payment Service
Handles PayPal orders and webhooks
"""
import os
import requests
from typing import Optional, Dict, Any
import base64

class PayPalService:
    """PayPal payment integration"""
    
    PRICE_USD = 25.00  # Lifetime access price
    
    def __init__(self):
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        self.mode = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
        
        # API URLs
        if self.mode == 'live':
            self.api_base = 'https://api-m.paypal.com'
        else:
            self.api_base = 'https://api-m.sandbox.paypal.com'
        
        if self.client_id and self.client_secret:
            print(f"✓ PayPal initialized ({self.mode} mode)")
        else:
            print("⚠ PayPal credentials not configured")
    
    def is_configured(self) -> bool:
        """Check if PayPal is properly configured"""
        return bool(self.client_id and self.client_secret)
    
    def _get_access_token(self) -> Optional[str]:
        """Get PayPal OAuth access token"""
        if not self.is_configured():
            return None
        
        try:
            auth = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            response = requests.post(
                f"{self.api_base}/v1/oauth2/token",
                headers={
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data='grant_type=client_credentials'
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
            else:
                print(f"PayPal auth error: {response.text}")
                return None
                
        except Exception as e:
            print(f"PayPal auth exception: {e}")
            return None
    
    def create_order(self, user_email: str, return_url: str, cancel_url: str) -> Optional[Dict[str, Any]]:
        """
        Create a PayPal order for one-time payment
        
        Args:
            user_email: Customer's email
            return_url: URL to redirect after approval
            cancel_url: URL to redirect if cancelled
            
        Returns:
            Dict with order_id and approval_url, or None on error
        """
        if not self.is_configured():
            raise Exception("PayPal is not configured")
        
        access_token = self._get_access_token()
        if not access_token:
            raise Exception("Failed to authenticate with PayPal")
        
        try:
            response = requests.post(
                f"{self.api_base}/v2/checkout/orders",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'intent': 'CAPTURE',
                    'purchase_units': [{
                        'amount': {
                            'currency_code': 'USD',
                            'value': str(self.PRICE_USD)
                        },
                        'description': 'Resume Maker - Lifetime Access',
                        'custom_id': user_email
                    }],
                    'application_context': {
                        'brand_name': 'Resume Maker',
                        'landing_page': 'BILLING',
                        'user_action': 'PAY_NOW',
                        'return_url': return_url,
                        'cancel_url': cancel_url
                    }
                }
            )
            
            if response.status_code in [200, 201]:
                order = response.json()
                approval_url = None
                for link in order.get('links', []):
                    if link.get('rel') == 'approve':
                        approval_url = link.get('href')
                        break
                
                return {
                    'order_id': order.get('id'),
                    'approval_url': approval_url,
                    'status': order.get('status')
                }
            else:
                print(f"PayPal order error: {response.text}")
                raise Exception("Failed to create PayPal order")
                
        except requests.RequestException as e:
            print(f"PayPal request error: {e}")
            raise Exception(f"Payment error: {str(e)}")
    
    def capture_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Capture (complete) a PayPal order after user approval
        
        Args:
            order_id: PayPal order ID
            
        Returns:
            Captured order details or None
        """
        if not self.is_configured():
            return None
        
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        try:
            response = requests.post(
                f"{self.api_base}/v2/checkout/orders/{order_id}/capture",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code in [200, 201]:
                capture = response.json()
                return {
                    'order_id': capture.get('id'),
                    'status': capture.get('status'),
                    'payer_email': capture.get('payer', {}).get('email_address'),
                    'custom_id': capture.get('purchase_units', [{}])[0].get('custom_id')
                }
            else:
                print(f"PayPal capture error: {response.text}")
                return None
                
        except Exception as e:
            print(f"PayPal capture exception: {e}")
            return None
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details"""
        if not self.is_configured():
            return None
        
        access_token = self._get_access_token()
        if not access_token:
            return None
        
        try:
            response = requests.get(
                f"{self.api_base}/v2/checkout/orders/{order_id}",
                headers={
                    'Authorization': f'Bearer {access_token}'
                }
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"PayPal get order error: {e}")
            return None

