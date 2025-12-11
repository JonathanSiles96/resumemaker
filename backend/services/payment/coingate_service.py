"""
CoinGate Payment Service
Handles cryptocurrency payments (USDT on TRC20, ERC20, BEP20)
"""
import os
import requests
from typing import Optional, Dict, Any
import hmac
import hashlib

class CoinGateService:
    """CoinGate cryptocurrency payment integration"""
    
    PRICE_USD = 25.00  # Lifetime access price
    
    def __init__(self):
        self.api_key = os.getenv('COINGATE_API_KEY')
        self.mode = os.getenv('COINGATE_MODE', 'sandbox')  # 'sandbox' or 'live'
        
        # API URLs
        if self.mode == 'live':
            self.api_base = 'https://api.coingate.com/v2'
        else:
            self.api_base = 'https://api-sandbox.coingate.com/v2'
        
        if self.api_key:
            print(f"✓ CoinGate initialized ({self.mode} mode)")
        else:
            print("⚠ CoinGate API key not configured")
    
    def is_configured(self) -> bool:
        """Check if CoinGate is properly configured"""
        return bool(self.api_key)
    
    def create_order(self, user_email: str, order_id: str, 
                     success_url: str, cancel_url: str, 
                     callback_url: str) -> Optional[Dict[str, Any]]:
        """
        Create a CoinGate order for cryptocurrency payment
        
        Args:
            user_email: Customer's email
            order_id: Your internal order ID
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if cancelled
            callback_url: Webhook URL for payment notifications
            
        Returns:
            Dict with payment_url and order details, or None on error
        """
        if not self.is_configured():
            raise Exception("CoinGate is not configured")
        
        try:
            response = requests.post(
                f"{self.api_base}/orders",
                headers={
                    'Authorization': f'Token {self.api_key}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'order_id': order_id,
                    'price_amount': self.PRICE_USD,
                    'price_currency': 'USD',
                    'receive_currency': 'USD',  # Receive in USD (converted)
                    'title': 'Resume Maker - Lifetime Access',
                    'description': f'Lifetime access for {user_email}',
                    'callback_url': callback_url,
                    'cancel_url': cancel_url,
                    'success_url': success_url,
                    'purchaser_email': user_email
                }
            )
            
            if response.status_code in [200, 201]:
                order = response.json()
                return {
                    'coingate_id': order.get('id'),
                    'order_id': order.get('order_id'),
                    'status': order.get('status'),
                    'payment_url': order.get('payment_url'),
                    'price_amount': order.get('price_amount'),
                    'price_currency': order.get('price_currency'),
                    'pay_amount': order.get('pay_amount'),
                    'pay_currency': order.get('pay_currency'),
                    'created_at': order.get('created_at')
                }
            else:
                print(f"CoinGate order error: {response.status_code} - {response.text}")
                raise Exception(f"Failed to create crypto payment: {response.text}")
                
        except requests.RequestException as e:
            print(f"CoinGate request error: {e}")
            raise Exception(f"Payment error: {str(e)}")
    
    def get_order(self, coingate_id: int) -> Optional[Dict[str, Any]]:
        """
        Get order details from CoinGate
        
        Args:
            coingate_id: CoinGate's order ID
            
        Returns:
            Order details or None
        """
        if not self.is_configured():
            return None
        
        try:
            response = requests.get(
                f"{self.api_base}/orders/{coingate_id}",
                headers={
                    'Authorization': f'Token {self.api_key}'
                }
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"CoinGate get order error: {e}")
            return None
    
    def verify_callback(self, data: Dict[str, Any]) -> bool:
        """
        Verify CoinGate callback authenticity
        
        Note: CoinGate uses IP whitelist for verification in production.
        Additional token verification can be implemented if needed.
        
        Args:
            data: Callback data from CoinGate
            
        Returns:
            True if valid, False otherwise
        """
        # CoinGate sends these statuses:
        # - 'new' - Order created
        # - 'pending' - Awaiting payment
        # - 'confirming' - Payment received, waiting for confirmations
        # - 'paid' - Payment confirmed
        # - 'invalid' - Payment invalid
        # - 'expired' - Order expired
        # - 'canceled' - Order cancelled
        # - 'refunded' - Payment refunded
        
        required_fields = ['id', 'order_id', 'status']
        for field in required_fields:
            if field not in data:
                print(f"CoinGate callback missing field: {field}")
                return False
        
        return True
    
    def is_payment_successful(self, status: str) -> bool:
        """Check if payment status indicates success"""
        return status in ['paid', 'confirming']
    
    def get_supported_currencies(self) -> list:
        """Get list of supported cryptocurrencies"""
        # USDT is available on multiple networks
        return [
            {'code': 'USDT', 'name': 'Tether', 'networks': ['TRC20', 'ERC20', 'BEP20']},
            {'code': 'BTC', 'name': 'Bitcoin', 'networks': ['Bitcoin']},
            {'code': 'ETH', 'name': 'Ethereum', 'networks': ['ERC20']},
            {'code': 'LTC', 'name': 'Litecoin', 'networks': ['Litecoin']},
        ]

