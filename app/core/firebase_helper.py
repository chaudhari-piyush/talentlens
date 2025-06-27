"""
Helper module to handle Firebase credentials in production
"""
import os
import json
import base64
import tempfile
from pathlib import Path


def get_firebase_credentials_path():
    """
    Get Firebase credentials path, handling different environments
    
    Returns:
        str: Path to Firebase credentials file
    """
    # First, check if we have a local credentials file
    local_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "app/config/ServiceAccountKey.json")
    if os.path.exists(local_path):
        return local_path
    
    # In production, check for base64 encoded credentials
    base64_creds = os.getenv("FIREBASE_CREDENTIALS_BASE64")
    if base64_creds:
        # Create a temporary file with the decoded credentials
        try:
            decoded_creds = base64.b64decode(base64_creds)
            creds_dict = json.loads(decoded_creds)
            
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.json')
            with os.fdopen(fd, 'w') as f:
                json.dump(creds_dict, f)
            
            return temp_path
        except Exception as e:
            print(f"Error decoding Firebase credentials: {e}")
    
    return None