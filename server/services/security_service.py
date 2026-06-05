#!/usr/bin/env python3
"""
Enhanced Security Service for Phase 5
Handles encryption, consent management, and data privacy
"""

import os
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityService:
    """Enhanced security service for data encryption and consent management"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key from environment or generate new one"""
        # Try to get key from environment
        key_str = os.getenv('ENCRYPTION_KEY')
        if key_str:
            try:
                return base64.urlsafe_b64decode(key_str.encode())
            except Exception:
                pass
        
        # Generate new key from JWT secret
        jwt_secret = os.getenv('JWT_SECRET', 'default_secret_key')
        salt = b'clare_careiq_salt_2024'  # Fixed salt for consistency
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(jwt_secret.encode()))
        return key
    
    def encrypt_field(self, data: str) -> str:
        """Encrypt a string field"""
        if not data:
            return ""
        
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return data  # Return original data if encryption fails
    
    def decrypt_field(self, encrypted_data: str) -> str:
        """Decrypt a string field"""
        if not encrypted_data:
            return ""
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return encrypted_data  # Return original data if decryption fails
    
    def hash_sensitive_data(self, data: str) -> str:
        """Create a hash of sensitive data for indexing/searching"""
        if not data:
            return ""
        
        return hashlib.sha256(data.encode()).hexdigest()[:16]  # First 16 chars for indexing

class ConsentManager:
    """Manages user consent for data processing"""
    
    CONSENT_TYPES = {
        'data_storage': 'Store and process my medical data',
        'ai_analysis': 'Use AI to analyze my medical reports and chat',
        'medical_history': 'Build and maintain my medical history',
        'personalization': 'Use my data to personalize AI responses',
        'data_sharing': 'Share anonymized data for research (optional)'
    }
    
    CONSENT_VERSIONS = {
        'v1.0': {
            'version': '1.0',
            'date': '2024-09-01',
            'description': 'Initial consent framework for Clare & CareIQ'
        }
    }
    
    @classmethod
    def create_consent_record(cls, user_id: str, consent_types: Dict[str, bool], 
                            version: str = 'v1.0') -> Dict:
        """Create a consent record for a user"""
        return {
            'userId': user_id,
            'consentTypes': consent_types,
            'version': version,
            'givenAt': datetime.utcnow(),
            'expiresAt': datetime.utcnow() + timedelta(days=365),  # 1 year
            'ipAddress': None,  # Could be added for audit trail
            'userAgent': None,  # Could be added for audit trail
            'status': 'active'
        }
    
    @classmethod
    def validate_consent(cls, consent_record: Dict, required_consent: str) -> bool:
        """Validate if user has given required consent"""
        if not consent_record:
            return False
        
        if consent_record.get('status') != 'active':
            return False
        
        if consent_record.get('expiresAt') < datetime.utcnow():
            return False
        
        return consent_record.get('consentTypes', {}).get(required_consent, False)
    
    @classmethod
    def get_consent_summary(cls, consent_record: Dict) -> Dict:
        """Get a summary of user's consent status"""
        if not consent_record:
            return {
                'hasConsent': False,
                'consentTypes': {},
                'status': 'no_consent',
                'message': 'No consent record found'
            }
        
        consent_types = consent_record.get('consentTypes', {})
        has_required = all([
            consent_types.get('data_storage', False),
            consent_types.get('ai_analysis', False),
            consent_types.get('medical_history', False),
            consent_types.get('personalization', False)
        ])
        
        return {
            'hasConsent': has_required,
            'consentTypes': consent_types,
            'version': consent_record.get('version'),
            'givenAt': consent_record.get('givenAt'),
            'expiresAt': consent_record.get('expiresAt'),
            'status': 'active' if has_required else 'incomplete',
            'message': 'Full consent given' if has_required else 'Incomplete consent'
        }

class DataPrivacyManager:
    """Manages data privacy and user rights"""
    
    @classmethod
    def anonymize_data(cls, data: Dict) -> Dict:
        """Anonymize data for research purposes"""
        anonymized = data.copy()
        
        # Remove or hash personal identifiers
        if 'userId' in anonymized:
            anonymized['userId'] = hashlib.sha256(anonymized['userId'].encode()).hexdigest()[:8]
        
        if 'email' in anonymized:
            anonymized['email'] = 'anonymized@example.com'
        
        if 'name' in anonymized:
            anonymized['name'] = 'Anonymous User'
        
        # Remove timestamps that could identify users
        if 'createdAt' in anonymized:
            anonymized['createdAt'] = anonymized['createdAt'].replace(hour=0, minute=0, second=0, microsecond=0)
        
        return anonymized
    
    @classmethod
    def get_user_data_summary(cls, user_data: list) -> Dict:
        """Get a summary of user's data for privacy dashboard"""
        return {
            'totalRecords': len(user_data),
            'dataTypes': list(set([item.get('sourceType', 'unknown') for item in user_data])),
            'dateRange': {
                'earliest': min([item.get('createdAt', datetime.utcnow()) for item in user_data]) if user_data else None,
                'latest': max([item.get('createdAt', datetime.utcnow()) for item in user_data]) if user_data else None
            },
            'encryptedFields': ['summaryText_enc', 'rawData'],
            'lastUpdated': datetime.utcnow()
        }

