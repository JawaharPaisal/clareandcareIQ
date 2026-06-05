import base64
import os
import hashlib
import secrets

class FieldEncryption:
    """Handle field-level encryption for sensitive medical data (simplified for Phase 1)"""
    
    def __init__(self):
        self.key = self._get_encryption_key()
    
    def _get_encryption_key(self):
        """Get encryption key from environment"""
        key_b64 = os.getenv('FIELD_ENC_KEY_BASE64')
        if not key_b64:
            return None
        
        try:
            return base64.b64decode(key_b64)
        except Exception:
            return None
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string field (simplified hash for Phase 1)"""
        if not plaintext:
            return plaintext
        
        try:
            # For Phase 1, use simple hashing instead of encryption
            # In Phase 5, we'll implement proper AES encryption
            hash_obj = hashlib.sha256(plaintext.encode('utf-8'))
            return f"HASHED_{hash_obj.hexdigest()[:32]}"
        except Exception:
            # If hashing fails, return original (for development)
            return plaintext
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt a string field (simplified for Phase 1)"""
        if not encrypted_text:
            return encrypted_text
        
        # For Phase 1, we can't decrypt hashed values
        # This is just a placeholder until we implement real encryption
        if encrypted_text.startswith("HASHED_"):
            return "[ENCRYPTED DATA - Phase 1 placeholder]"
        
        return encrypted_text

# Global instance
field_encryption = FieldEncryption()

def generate_encryption_key() -> str:
    """Generate a new encryption key for FIELD_ENC_KEY_BASE64"""
    # For Phase 1, generate a simple key
    # In Phase 5, we'll use proper cryptographic keys
    key = secrets.token_bytes(32)
    return base64.b64encode(key).decode('utf-8')

def validate_medical_data(data: dict) -> dict:
    """Validate and sanitize medical data input"""
    # Basic validation - extend as needed
    validated = {}
    
    # Text fields - strip and limit length
    text_fields = ['summaryText', 'notes', 'description']
    for field in text_fields:
        if field in data:
            value = str(data[field]).strip()
            validated[field] = value[:5000]  # Max 5000 chars
    
    # Array fields - ensure they're lists
    array_fields = ['conditions', 'allergies', 'medications', 'tags']
    for field in array_fields:
        if field in data:
            if isinstance(data[field], list):
                # Limit to 50 items, each max 100 chars
                validated[field] = [str(item)[:100] for item in data[field][:50]]
            else:
                validated[field] = []
    
    # Object fields - ensure they're dicts
    object_fields = ['vitals', 'labs', 'extracted']
    for field in object_fields:
        if field in data:
            if isinstance(data[field], dict):
                validated[field] = data[field]
            else:
                validated[field] = {}
    
    return validated
