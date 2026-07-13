# Code Changes & Risk Analysis

Real ServiceNow code examples showing how changes correlate to risk levels.

## 1. LOW RISK: Authentication Service Update

### Change Summary
- **Files Changed**: 3
- **Lines Changed**: 120 (+80, -40)
- **Developers**: 1 (Senior)
- **Test Coverage**: 95%
- **Risk Score**: 18% 🟢 LOW

### Why Low Risk?
✓ Minimal code churn (3 files)
✓ Senior developer with auth expertise
✓ High test coverage maintained
✓ Simple, well-established authentication pattern
✓ No external dependencies affected

### Before Code

**auth_service.py (Original)**
```python
class AuthService:
    """ServiceNow Authentication Handler"""
    
    def verify_token(self, token):
        if not token:
            return False
        
        payload = self.decode_token(token)
        user = self.get_user(payload['user_id'])
        
        if user and user.is_active:
            return True
        return False
    
    def decode_token(self, token):
        return jwt.decode(token, self.secret_key)
```

### After Code

**auth_service.py (Updated)**
```python
class AuthService:
    """ServiceNow Authentication Handler with Token Expiry"""
    
    def verify_token(self, token, max_age=3600):
        if not token:
            return False
        
        payload = self.decode_token(token)
        user = self.get_user(payload['user_id'])
        
        # NEW: Check token expiry
        if payload['exp'] < time.time():
            self.logger.info(f"Token expired for user {payload['user_id']}")
            return False
        
        if user and user.is_active:
            return True
        return False
    
    def decode_token(self, token, max_age=3600):
        return jwt.decode(token, self.secret_key, algorithms=['HS256'])
```

### Changes Made
- Added token expiry validation
- Added logging for expired tokens
- Explicit algorithm specification in JWT decode
- 40 lines added, 0 lines removed

### Tests Added
```python
def test_verify_token_expired():
    auth = AuthService()
    expired_token = create_expired_token()
    assert not auth.verify_token(expired_token)

def test_verify_token_invalid_algorithm():
    auth = AuthService()
    tampered_token = create_tampered_token()
    assert not auth.verify_token(tampered_token)
```

### Risk Assessment

| Factor | Impact |
|--------|--------|
| Isolated change to auth service | ✓ Reduces risk |
| Senior developer, known pattern | ✓ Reduces risk |
| Comprehensive tests added | ✓ Reduces risk |
| No API changes | ✓ Reduces risk |
| Backward compatible | ✓ Reduces risk |
| **Overall Risk**: 18% | 🟢 LOW |

### Suggested Testing
```
✓ Run: Auth Module Regression Suite (30 min)
✓ Focus: Token validation edge cases
✓ Manual: Login flow happy path
```

---

## 2. MEDIUM RISK: Incident Management Workflow

### Change Summary
- **Files Changed**: 7
- **Lines Changed**: 250 (+200, -50)
- **Developers**: 2 (1 mid-level + 1 junior)
- **Test Coverage**: 68%
- **Open Defects in Module**: 2
- **Risk Score**: 55% 🟠 MEDIUM

### Why Medium Risk?
⚠️ Multiple files changed across workflow
⚠️ Mixed experience levels
⚠️ Moderate test coverage
⚠️ Module has existing open issues
✓ Well-defined scope (incident management only)

### Before Code

**incident_processor.py (Original)**
```python
class IncidentProcessor:
    """ServiceNow Incident Processing"""
    
    def create_incident(self, title, description, severity):
        incident = {
            'title': title,
            'description': description,
            'severity': severity,
            'status': 'New',
            'created_at': datetime.now()
        }
        
        self.db.insert('incidents', incident)
        self.notify_team(incident)
        return incident
    
    def notify_team(self, incident):
        # Send email to team
        email = EmailService()
        email.send(f"New incident: {incident['title']}")
```

### After Code

**incident_processor.py (Updated)**
```python
class IncidentProcessor:
    """ServiceNow Incident Processing with SLA & Routing"""
    
    def create_incident(self, title, description, severity):
        incident = {
            'title': title,
            'description': description,
            'severity': severity,
            'status': 'New',
            'sla_deadline': self.calculate_sla(severity),  # NEW
            'assigned_group': self.route_incident(severity),  # NEW
            'created_at': datetime.now()
        }
        
        self.db.insert('incidents', incident)
        self.notify_team(incident)
        self.escalate_if_needed(incident)  # NEW
        return incident
    
    def calculate_sla(self, severity):
        """Calculate SLA deadline based on severity"""
        sla_hours = {'Critical': 1, 'High': 4, 'Medium': 8, 'Low': 24}
        return datetime.now() + timedelta(hours=sla_hours[severity])
    
    def route_incident(self, severity):
        """Route incident to appropriate team"""
        routing = {
            'Critical': 'network_ops',
            'High': 'platform_team',
            'Medium': 'application_team',
            'Low': 'support_team'
        }
        return routing.get(severity, 'support_team')
    
    def escalate_if_needed(self, incident):
        """Escalate critical incidents"""
        if incident['severity'] == 'Critical':
            self.notify_manager()
            self.create_war_room()

    def notify_team(self, incident):
        # Send email + Slack notification
        email = EmailService()
        email.send(f"New incident: {incident['title']}")
        
        slack = SlackService()  # NEW
        slack.notify(
            channel=f"#{incident['assigned_group']}",
            message=f"Incident {incident['id']}: {incident['title']}"
        )
```

### New Files Created
- `sla_manager.py` - SLA tracking logic
- `incident_router.py` - Routing logic
- `tests/test_incident_routing.py` - Tests for new routing

### Risk Factors

| Factor | Impact |
|--------|--------|
| Multiple files touched (7) | ⚠️ Medium risk |
| New routing logic introduced | ⚠️ Medium risk |
| SLA calculations (timing-dependent) | ⚠️ Medium risk |
| Mixed developer experience | ⚠️ Medium risk |
| Integration with Slack API | ⚠️ Medium risk (new dependency) |
| Module has 2 open defects | ⚠️ Medium risk |
| 68% test coverage | ✓ Partial coverage |
| Backward compatible | ✓ Reduces risk |
| **Overall Risk**: 55% | 🟠 MEDIUM |

### Suggested Testing
```
⚠️ PRIORITY 1: Incident Management Regression Suite (45 min)
  - Create incidents with each severity level
  - Verify SLA calculations
  - Check routing assignments
  - Validate Slack notifications

⚠️ PRIORITY 2: Manual UAT (1 hour)
  - End-to-end workflow: Create → Route → Escalate → Resolve
  - Test with actual Slack integration
  - Verify email + Slack notifications both sent

⚠️ PRIORITY 3: Integration Tests
  - Slack API integration
  - Database transaction rollback scenarios
  - Handle missing routing config gracefully
```

---

## 3. HIGH RISK: Payment Gateway Integration

### Change Summary
- **Files Changed**: 14
- **Lines Changed**: 780 (+650, -130)
- **Developers**: 2 (both junior)
- **Test Coverage**: 45%
- **External Dependencies**: 3 new (Stripe, PayPal, fraud detection)
- **Days to Release**: 5
- **Open Defects in Module**: 3
- **Risk Score**: 87% 🔴 HIGH

### Why High Risk?
🔴 Large code changes across payment system
🔴 Junior developers, first-time payment experience
🔴 Low test coverage in payment module
🔴 Multiple new external dependencies
🔴 Tight release timeline (5 days)
🔴 Module has existing open defects
🔴 Handles sensitive financial data

### Before Code

**payment_gateway.py (Original)**
```python
class PaymentGateway:
    """ServiceNow Payment Processing - Basic"""
    
    def process_payment(self, order_id, amount, card_token):
        try:
            # Simple payment processing
            transaction = {
                'order_id': order_id,
                'amount': amount,
                'status': 'pending',
                'timestamp': datetime.now()
            }
            
            self.db.insert('transactions', transaction)
            self.call_payment_provider(card_token, amount)
            
            transaction['status'] = 'completed'
            self.db.update('transactions', transaction)
            
            return transaction
        except Exception as e:
            self.logger.error(f"Payment failed: {e}")
            return None
```

### After Code

**payment_gateway.py (Updated - MULTI-PROVIDER)**
```python
from stripe import StripeClient
from paypal import PayPalClient
from fraud_detection import FraudAnalyzer

class PaymentGateway:
    """ServiceNow Payment Processing - Multi-Provider with Fraud Detection"""
    
    def __init__(self):
        self.stripe = StripeClient(api_key=os.environ['STRIPE_KEY'])
        self.paypal = PayPalClient(api_key=os.environ['PAYPAL_KEY'])
        self.fraud_analyzer = FraudAnalyzer()
    
    def process_payment(self, order_id, amount, card_token, customer_info):
        try:
            # NEW: Fraud check
            if self.fraud_analyzer.is_suspicious(customer_info, amount):
                return {'status': 'fraud_blocked', 'order_id': order_id}
            
            transaction = {
                'order_id': order_id,
                'amount': amount,
                'currency': 'USD',
                'status': 'pending',
                'provider': self.select_provider(customer_info),  # NEW
                'timestamp': datetime.now()
            }
            
            self.db.insert('transactions', transaction)
            
            # NEW: Provider selection logic
            if transaction['provider'] == 'stripe':
                result = self.process_stripe_payment(card_token, amount)
            elif transaction['provider'] == 'paypal':
                result = self.process_paypal_payment(customer_info, amount)
            else:
                return {'status': 'error', 'message': 'No provider available'}
            
            # NEW: Comprehensive transaction logging
            transaction.update({
                'status': result['status'],
                'provider_id': result.get('provider_id'),
                'receipt_url': result.get('receipt'),
                'completed_at': datetime.now()
            })
            
            self.db.update('transactions', transaction)
            self.send_receipt(customer_info['email'], transaction)  # NEW
            
            return transaction
            
        except StripeError as e:
            self.handle_stripe_error(e, order_id)
            return {'status': 'stripe_error', 'order_id': order_id}
        except PayPalError as e:
            self.handle_paypal_error(e, order_id)
            return {'status': 'paypal_error', 'order_id': order_id}
        except Exception as e:
            self.logger.error(f"Payment failed: {str(e)}")
            self.alert_ops_team(order_id, str(e))  # NEW
            return {'status': 'unknown_error', 'order_id': order_id}
    
    def select_provider(self, customer_info):
        """NEW: Provider selection logic"""
        if customer_info.get('preferred_provider') == 'paypal':
            return 'paypal'
        return 'stripe'  # Default
    
    def process_stripe_payment(self, card_token, amount):
        """NEW: Stripe-specific logic"""
        charge = self.stripe.charges.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            source=card_token
        )
        return {
            'status': 'completed',
            'provider_id': charge.id,
            'receipt': charge.receipt_url
        }
    
    def process_paypal_payment(self, customer_info, amount):
        """NEW: PayPal-specific logic"""
        payment = self.paypal.payments.create(
            intent='sale',
            payer={'email': customer_info['email']},
            amount={'total': str(amount), 'currency': 'USD'}
        )
        return {
            'status': 'completed',
            'provider_id': payment.id,
            'receipt': payment.links[0].href
        }
    
    def send_receipt(self, email, transaction):
        """NEW: Email receipt to customer"""
        receipt_email = EmailService()
        receipt_email.send_receipt(email, transaction)
    
    def handle_stripe_error(self, error, order_id):
        """NEW: Stripe error handling"""
        self.logger.error(f"Stripe error for order {order_id}: {error}")
        self.db.update_transaction_status(order_id, 'failed')
    
    def handle_paypal_error(self, error, order_id):
        """NEW: PayPal error handling"""
        self.logger.error(f"PayPal error for order {order_id}: {error}")
        self.db.update_transaction_status(order_id, 'failed')
    
    def alert_ops_team(self, order_id, error_msg):
        """NEW: Alert operations on unexpected errors"""
        slack = SlackService()
        slack.send_alert(f"Payment processing error for order {order_id}: {error_msg}")
```

### New Files Created
- `payment_providers/stripe_handler.py` - Stripe integration
- `payment_providers/paypal_handler.py` - PayPal integration
- `fraud_detection.py` - Fraud detection logic
- `tests/test_payment_processing.py` - Payment tests (INCOMPLETE)
- `tests/test_fraud_detection.py` - Fraud tests (INCOMPLETE)
- `tests/integration/test_stripe_api.py` - Stripe API integration tests

### High-Risk Indicators

| Factor | Impact | Severity |
|--------|--------|----------|
| **14 files changed** | Large surface area | 🔴 CRITICAL |
| **650 lines added** | Significant code complexity | 🔴 CRITICAL |
| **2 junior developers** | Limited payment expertise | 🔴 CRITICAL |
| **First-time with payment APIs** | New complexity | 🔴 CRITICAL |
| **Only 45% test coverage** | Many untested paths | 🔴 CRITICAL |
| **3 new external APIs** | Multiple failure points | 🔴 CRITICAL |
| **Handles financial data** | Regulatory/security risk | 🔴 CRITICAL |
| **5 days to release** | Rushed, no buffer | 🔴 CRITICAL |
| **Existing open defects** | Module already problematic | 🔴 CRITICAL |
| **No fraud detection before** | New attack surface | 🔴 CRITICAL |
| **Overall Risk**: 87% | HIGH RISK | 🔴 CRITICAL |

### Critical Issues Identified

```
⚠️ RISK ALERT: DO NOT MERGE WITHOUT:

1. CODE REVIEW
   - [ ] Payment security review by senior engineer
   - [ ] Fraud detection logic review
   - [ ] API error handling review
   - [ ] PCI compliance review

2. TESTING (Currently incomplete)
   - [ ] Unit tests for Stripe integration
   - [ ] Unit tests for PayPal integration
   - [ ] Unit tests for fraud detection
   - [ ] Integration tests with both providers
   - [ ] End-to-end payment flow tests
   - [ ] Error scenario testing (declined cards, timeouts, etc.)
   - [ ] Fraud detection false positive rate < 2%

3. SECURITY
   - [ ] No hardcoded API keys
   - [ ] No sensitive data in logs
   - [ ] PCI DSS compliance verified
   - [ ] SSL certificate for API calls verified
   - [ ] Rate limiting implemented
   - [ ] OWASP top 10 review completed

4. PERFORMANCE
   - [ ] Load test with 1000 concurrent payments
   - [ ] Fraud check latency < 200ms
   - [ ] Payment processing latency < 5s
   - [ ] Database query optimization verified

5. PRODUCTION READINESS
   - [ ] Rollback plan documented
   - [ ] Canary deployment for 5% of traffic
   - [ ] On-call team briefed
   - [ ] Monitoring/alerts set up for errors
   - [ ] Historical data migration tested
```

### Recommended Release Strategy

```
RECOMMENDATION: EXTENDED TESTING + PHASED ROLLOUT

PHASE 1: Extended QA (3 days)
├── Run full payment regression suite (8 hours)
├── New fraud detection testing (4 hours)
├── Multi-provider load testing (4 hours)
├── Security review by external team (2 days)
└── Fix critical issues found

PHASE 2: Canary Deployment (Day 4)
├── Deploy to 5% of production traffic
├── Monitor for 24 hours
├── Error rate threshold: < 0.5%
├── If successful, proceed to Phase 3

PHASE 3: Staged Rollout (Day 5)
├── 10:00 AM: Deploy to 25% of traffic
├── Monitor for 2 hours
├── 12:00 PM: Deploy to 50% of traffic
├── Monitor for 2 hours
├── 2:00 PM: Deploy to 100% of traffic
├── On-call engineer standing by for 4 hours
```

### Suggested Testing Checklist

```
✓ PRIORITY 1: Payment Processing (Critical)
  - Stripe payment success flow
  - PayPal payment success flow
  - Declined card handling
  - Network timeout handling
  - Invalid currency handling
  - Concurrent payment processing

✓ PRIORITY 2: Fraud Detection (Critical)
  - Normal transaction acceptance
  - Suspicious pattern detection
  - False positive rate measurement
  - Large amount detection
  - Velocity checks

✓ PRIORITY 3: Integration (High)
  - Receipt email delivery
  - Transaction logging accuracy
  - Database consistency
  - API error propagation

✓ PRIORITY 4: Error Handling (High)
  - Provider downtime simulation
  - Partial failure recovery
  - Error notification to ops team
  - Transaction state recovery
```

---

## Risk Summary Table

| Aspect | Low Risk | Medium Risk | High Risk |
|--------|----------|-----------|----------|
| **Files Changed** | 1-3 | 4-8 | 9+ |
| **Lines Changed** | 0-100 | 100-500 | 500+ |
| **Developer Experience** | Senior | Mid-level | Junior |
| **Test Coverage** | 80%+ | 50-80% | <50% |
| **External Dependencies** | 0 | 1-2 | 3+ |
| **Module History** | Stable | Some issues | Defect-prone |
| **Financial Impact** | Low | Medium | High |
| **Time to Release** | 14+ days | 7-14 days | <7 days |

---

## Key Takeaway

The difference between these three examples demonstrates how the Risk Prediction Module combines multiple factors to provide actionable guidance:

- **Low Risk**: Deploy immediately with quick sanity check
- **Medium Risk**: Extended regression testing + manual UAT
- **High Risk**: Full QA cycle + security review + canary deployment + on-call backup

This structured approach helps QA teams allocate testing resources efficiently based on actual risk levels.
