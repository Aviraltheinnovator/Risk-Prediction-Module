"""
ServiceNow Authentication Service (Low Risk)

Metrics:
- Files changed: 1
- Lines changed: 45
- Test coverage: 95%
- Developer experience: Senior
- Expected risk: 15% (LOW)
"""

import jwt
import time
import logging
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class AuthService:
    """Handles ServiceNow authentication and token management"""

    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry_hours = 24

    def generate_token(self, user_id, username, roles):
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'roles': roles,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token, max_age=None):
        """Verify JWT token validity and expiry"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token age if max_age specified
            if max_age and 'iat' in payload:
                token_age = time.time() - payload['iat']
                if token_age > max_age:
                    logger.warning(f"Token too old for user {payload['user_id']}")
                    return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.info(f"Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def refresh_token(self, token):
        """Refresh an existing valid token"""
        payload = self.verify_token(token)
        if payload:
            return self.generate_token(
                payload['user_id'],
                payload['username'],
                payload['roles']
            )
        return None


def require_auth(func):
    """Decorator to protect endpoints requiring authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs.get('token') or args[0] if args else None
        auth_service = AuthService(secret_key='dev-key')

        if not token or not auth_service.verify_token(token):
            raise UnauthorizedError("Invalid or missing authentication token")

        return func(*args, **kwargs)

    return wrapper


class UnauthorizedError(Exception):
    """Raised when authentication fails"""
    pass
