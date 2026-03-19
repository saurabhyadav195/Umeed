import os
import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import json

def initialize_firebase():
    try:
        firebase_admin.get_app()
    except ValueError:
        # Check for JSON string in environment variable first (Production)
        firebase_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        
        if firebase_json:
            try:
                # Parse the JSON string
                service_account_info = json.loads(firebase_json)
                cred = credentials.Certificate(service_account_info)
            except json.JSONDecodeError as e:
                print(f"Error parsing FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
                # Fallback or exit gracefully
                return
        else:
            # Fallback to local file (Development)
            if os.path.exists(settings.FIREBASE_SERVICE_ACCOUNT_PATH):
                cred = credentials.Certificate(str(settings.FIREBASE_SERVICE_ACCOUNT_PATH))
            else:
                print("Firebase credentials not found (JSON string or file).")
                return
            
        firebase_admin.initialize_app(cred)

# Trigger initialization
initialize_firebase()