# Payment System Documentation

## Overview

The Resume Maker application includes a payment system that allows:
- **Free Tier**: 1 free resume generation for new users
- **Paid Tier**: $25 one-time payment for unlimited lifetime access

## Payment Providers

### 1. Stripe (Credit/Debit Cards)
- Handles card payments via Stripe Checkout
- Secure, PCI compliant
- Supports all major credit/debit cards

### 2. PayPal
- Popular payment method
- Supports PayPal balance and linked cards
- Available in sandbox and live modes

### 3. CoinGate (Cryptocurrency)
- Supports USDT on multiple networks:
  - TRC20 (Tron) - Lowest fees
  - ERC20 (Ethereum)
  - BEP20 (BSC)
- Also supports BTC, ETH, LTC

## Configuration

### Environment Variables

Add these to your `backend/.env` file:

```env
# ============== PAYMENT CONFIGURATION ==============

# Stripe (https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLIC_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# PayPal (https://developer.paypal.com/dashboard/applications)
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx
PAYPAL_MODE=live  # or 'sandbox' for testing

# CoinGate (https://coingate.com/merchant/api)
COINGATE_API_KEY=xxx
COINGATE_MODE=live  # or 'sandbox' for testing

# Application URL (for payment redirects)
APP_URL=https://yourdomain.com
```

## Setting Up Payment Providers

### Stripe Setup

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Create an account or log in
3. Get your API keys from **Developers → API Keys**
4. For webhooks:
   - Go to **Developers → Webhooks**
   - Add endpoint: `https://yourdomain.com/api/payment/stripe/webhook`
   - Select event: `checkout.session.completed`
   - Copy the webhook signing secret

### PayPal Setup

1. Go to [PayPal Developer](https://developer.paypal.com)
2. Create an app in **My Apps & Credentials**
3. Choose Sandbox for testing, Live for production
4. Copy Client ID and Secret

### CoinGate Setup

1. Go to [CoinGate](https://coingate.com)
2. Create a merchant account
3. Go to **API → API Keys**
4. Create a new API key with payment permissions
5. For testing, use sandbox: https://sandbox.coingate.com

## API Endpoints

### User Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/user/register` | POST | Register/identify user by email |
| `/api/user/status` | POST | Get user payment status |
| `/api/user/check-access` | POST | Check if user can generate |

### Payment Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/payment/config` | GET | Get payment configuration |
| `/api/payment/stripe/create-session` | POST | Create Stripe checkout |
| `/api/payment/stripe/webhook` | POST | Stripe webhook handler |
| `/api/payment/stripe/verify` | POST | Verify Stripe payment |
| `/api/payment/paypal/create-order` | POST | Create PayPal order |
| `/api/payment/paypal/capture-order` | POST | Capture PayPal payment |
| `/api/payment/coingate/create-order` | POST | Create crypto payment |
| `/api/payment/coingate/webhook` | POST | CoinGate webhook |
| `/api/payment/coingate/check` | POST | Check crypto payment status |

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_paid BOOLEAN DEFAULT FALSE,
    free_used BOOLEAN DEFAULT FALSE,
    total_generations INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    paid_at DATETIME
);
```

### Payments Table
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount FLOAT NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    provider VARCHAR(50) NOT NULL,
    provider_payment_id VARCHAR(255),
    provider_order_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    crypto_currency VARCHAR(20),
    crypto_network VARCHAR(20),
    crypto_amount VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME,
    completed_at DATETIME
);
```

## User Flow

```
┌─────────────────┐
│   New User      │
│  Enters Email   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  First Resume   │
│     FREE!       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Wants More?    │────▶│  Payment Modal  │
│  Pay $25        │     │  Stripe/PayPal  │
└─────────────────┘     │  /Crypto        │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   UNLIMITED     │
                        │   FOREVER!      │
                        └─────────────────┘
```

## Testing

### Test Mode

Use sandbox/test credentials for development:

**Stripe Test Card:**
- Number: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits

**PayPal Sandbox:**
- Use sandbox accounts from PayPal Developer Dashboard

**CoinGate Sandbox:**
- Use sandbox API at `https://sandbox.coingate.com`

### Testing Webhooks Locally

Use ngrok to expose your local server:

```bash
ngrok http 5000
```

Then update webhook URLs in payment provider dashboards.

## Security Considerations

1. **Never expose secret keys** in frontend code
2. **Validate webhooks** using signatures
3. **Use HTTPS** in production
4. **Store payment data** securely
5. **Log transactions** for auditing

## Troubleshooting

### Payment Not Completing

1. Check webhook configuration
2. Verify API keys are correct
3. Check server logs: `pm2 logs resumemaker`
4. Verify database is writable

### User Not Marked as Paid

1. Check webhook received: Look in logs
2. Manually update: Use database admin tool
3. Verify payment in provider dashboard

### Crypto Payment Stuck

1. CoinGate may take time for confirmations
2. Check payment status in CoinGate dashboard
3. Webhook should update automatically

## Support

For payment issues:
- Stripe: support@stripe.com
- PayPal: PayPal Resolution Center
- CoinGate: support@coingate.com

---

**Last Updated**: December 2025
**Version**: 1.0

