"""
ServiceNow Payment Gateway Integration (High Risk)

Metrics:
- Files changed: 14
- Lines changed: 780
- Test coverage: 45%
- Developer experience: 2 junior
- External dependencies: 3 new (Stripe, PayPal, fraud detection)
- Days to release: 5
- Open defects: 3
- Expected risk: 87% (HIGH)

⚠️ WARNING: This module handles sensitive financial data and requires:
   - Security review before deployment
   - Extended QA testing
   - Phased rollout with canary deployment
"""

import os
import logging
import json
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PaymentProvider(Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"


class TransactionStatus(Enum):
    """Transaction states"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    FRAUD_BLOCKED = "fraud_blocked"
    REFUNDED = "refunded"


class FraudDetectionService:
    """Analyzes transactions for fraud indicators"""

    FRAUD_THRESHOLDS = {
        'large_amount': 5000,
        'velocity_limit': 10,  # transactions per hour
        'same_card_limit': 3   # transactions per hour
    }

    def __init__(self, ml_model_path: Optional[str] = None):
        self.ml_model = self._load_model(ml_model_path) if ml_model_path else None
        self.suspicious_patterns = []

    def is_suspicious(self, customer_info: Dict, amount: float) -> Tuple[bool, str]:
        """Detect suspicious transaction patterns"""

        reason = ""

        # Check for large amounts
        if amount > self.FRAUD_THRESHOLDS['large_amount']:
            reason = "Large transaction amount"
            return True, reason

        # Check velocity
        velocity = self._check_velocity(customer_info['email'])
        if velocity > self.FRAUD_THRESHOLDS['velocity_limit']:
            reason = f"High velocity: {velocity} transactions/hour"
            return True, reason

        # Check if ML model detects fraud
        if self.ml_model and self._predict_fraud(customer_info, amount):
            reason = "ML model detected fraud indicators"
            return True, reason

        return False, ""

    def _check_velocity(self, email: str) -> int:
        """Check transaction velocity for email"""
        # TODO: Query last hour transactions for this email
        return 0

    def _predict_fraud(self, customer_info: Dict, amount: float) -> bool:
        """Use ML model to predict fraud"""
        if not self.ml_model:
            return False

        features = self._extract_features(customer_info, amount)
        return self.ml_model.predict(features)

    def _extract_features(self, customer_info: Dict, amount: float) -> Dict:
        """Extract features for ML model"""
        return {
            'amount': amount,
            'time_of_day': datetime.now().hour,
            'customer_age': customer_info.get('age', 0),
            'account_age_days': customer_info.get('account_age_days', 0)
        }

    def _load_model(self, path: str):
        """Load fraud detection ML model"""
        try:
            import pickle
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load fraud model: {e}")
            return None


class PaymentProviderClient(ABC):
    """Abstract base for payment provider integrations"""

    @abstractmethod
    def charge(self, amount: float, token: str, metadata: Dict) -> Dict:
        """Process a charge with the provider"""
        pass

    @abstractmethod
    def refund(self, provider_id: str, amount: float) -> Dict:
        """Refund a transaction"""
        pass


class StripeClient(PaymentProviderClient):
    """Stripe payment processing integration"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Stripe API key not configured")
        self.api_key = api_key
        # In production, use: import stripe; stripe.api_key = api_key

    def charge(self, amount: float, token: str, metadata: Dict) -> Dict:
        """Process Stripe charge"""
        try:
            # TODO: Replace with actual Stripe API call
            # charge = stripe.Charge.create(
            #     amount=int(amount * 100),  # Convert to cents
            #     currency='usd',
            #     source=token,
            #     metadata=metadata
            # )

            return {
                'status': 'completed',
                'provider_id': f'ch_stripe_{int(datetime.now().timestamp())}',
                'receipt_url': 'https://pay.stripe.com/receipts/test',
                'error': None
            }
        except Exception as e:
            logger.error(f"Stripe charge failed: {e}")
            return {'status': 'failed', 'error': str(e), 'provider_id': None}

    def refund(self, provider_id: str, amount: float) -> Dict:
        """Refund Stripe charge"""
        try:
            # TODO: Replace with actual Stripe API call
            return {'status': 'refunded', 'refund_id': f'ref_{provider_id}'}
        except Exception as e:
            logger.error(f"Stripe refund failed: {e}")
            return {'status': 'failed', 'error': str(e)}


class PayPalClient(PaymentProviderClient):
    """PayPal payment processing integration"""

    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not client_secret:
            raise ValueError("PayPal credentials not configured")
        self.client_id = client_id
        self.client_secret = client_secret

    def charge(self, amount: float, token: str, metadata: Dict) -> Dict:
        """Process PayPal charge"""
        try:
            # TODO: Replace with actual PayPal API call
            return {
                'status': 'completed',
                'provider_id': f'paypal_{int(datetime.now().timestamp())}',
                'receipt_url': 'https://paypal.com/receipts/test',
                'error': None
            }
        except Exception as e:
            logger.error(f"PayPal charge failed: {e}")
            return {'status': 'failed', 'error': str(e), 'provider_id': None}

    def refund(self, provider_id: str, amount: float) -> Dict:
        """Refund PayPal charge"""
        try:
            return {'status': 'refunded', 'refund_id': f'ref_{provider_id}'}
        except Exception as e:
            logger.error(f"PayPal refund failed: {e}")
            return {'status': 'failed', 'error': str(e)}


class PaymentGateway:
    """Main payment processing orchestrator"""

    def __init__(self, db_client, stripe_key: str, paypal_id: str, paypal_secret: str):
        self.db = db_client
        self.stripe = StripeClient(stripe_key) if stripe_key else None
        self.paypal = PayPalClient(paypal_id, paypal_secret) if paypal_id else None
        self.fraud_analyzer = FraudDetectionService()

    def process_payment(self, order_id: str, amount: float, card_token: str,
                       customer_info: Dict) -> Dict:
        """Main payment processing entry point"""

        # 1. Fraud check
        is_suspicious, reason = self.fraud_analyzer.is_suspicious(customer_info, amount)
        if is_suspicious:
            logger.warning(f"Fraud detected for order {order_id}: {reason}")
            return self._create_transaction(order_id, amount, TransactionStatus.FRAUD_BLOCKED, reason)

        # 2. Create transaction record
        transaction = self._create_transaction(order_id, amount, TransactionStatus.PENDING)

        # 3. Determine provider
        provider = self._select_provider(customer_info)

        try:
            # 4. Process charge
            if provider == PaymentProvider.STRIPE and self.stripe:
                result = self.stripe.charge(amount, card_token, {'order_id': order_id})
            elif provider == PaymentProvider.PAYPAL and self.paypal:
                result = self.paypal.charge(amount, card_token, {'order_id': order_id})
            else:
                return self._create_transaction(order_id, amount, TransactionStatus.FAILED, "No payment provider available")

            # 5. Update transaction
            if result['status'] == 'completed':
                transaction = self._create_transaction(
                    order_id, amount, TransactionStatus.COMPLETED,
                    provider_id=result['provider_id'],
                    receipt_url=result['receipt_url']
                )
                self._send_receipt(customer_info['email'], transaction)
            else:
                transaction = self._create_transaction(order_id, amount, TransactionStatus.FAILED, result['error'])

        except Exception as e:
            logger.error(f"Payment processing exception: {e}")
            self._alert_ops_team(order_id, str(e))
            transaction = self._create_transaction(order_id, amount, TransactionStatus.FAILED, str(e))

        return transaction

    def refund_payment(self, order_id: str) -> Dict:
        """Refund a processed transaction"""
        transaction = self.db.get('transactions', order_id)

        if not transaction:
            return {'status': 'failed', 'error': f"Transaction {order_id} not found"}

        if transaction['status'] != 'completed':
            return {'status': 'failed', 'error': "Can only refund completed transactions"}

        provider = transaction.get('provider', PaymentProvider.STRIPE.value)
        provider_id = transaction.get('provider_id')

        try:
            if provider == PaymentProvider.STRIPE.value and self.stripe:
                result = self.stripe.refund(provider_id, transaction['amount'])
            elif provider == PaymentProvider.PAYPAL.value and self.paypal:
                result = self.paypal.refund(provider_id, transaction['amount'])
            else:
                return {'status': 'failed', 'error': "Provider not available"}

            transaction['status'] = TransactionStatus.REFUNDED.value
            self.db.update('transactions', transaction)

            return result
        except Exception as e:
            logger.error(f"Refund failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _select_provider(self, customer_info: Dict) -> PaymentProvider:
        """Select payment provider based on customer preference"""
        preferred = customer_info.get('preferred_payment_method')
        if preferred == 'paypal' and self.paypal:
            return PaymentProvider.PAYPAL
        return PaymentProvider.STRIPE

    def _create_transaction(self, order_id: str, amount: float,
                           status: TransactionStatus, reason: str = "",
                           provider_id: str = "", receipt_url: str = "") -> Dict:
        """Create or update transaction record"""
        transaction = {
            'order_id': order_id,
            'amount': amount,
            'currency': 'USD',
            'status': status.value,
            'reason': reason,
            'provider_id': provider_id,
            'receipt_url': receipt_url,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        self.db.insert('transactions', transaction)
        return transaction

    def _send_receipt(self, email: str, transaction: Dict):
        """Send receipt to customer"""
        try:
            # TODO: Implement receipt email
            logger.info(f"Receipt sent to {email} for transaction {transaction['order_id']}")
        except Exception as e:
            logger.error(f"Failed to send receipt: {e}")

    def _alert_ops_team(self, order_id: str, error_msg: str):
        """Alert operations team on critical errors"""
        try:
            # TODO: Send Slack/PagerDuty alert
            logger.error(f"OPS ALERT: Payment processing error for {order_id}: {error_msg}")
        except Exception as e:
            logger.error(f"Failed to alert ops team: {e}")
