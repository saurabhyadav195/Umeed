import os
import firebase_admin
from firebase_admin import credentials, storage

def verify_storage():
    service_account_path = "firebase-service-account.json"
    bucket_name = "umeed-f2657.firebasestorage.app"

    if not os.path.exists(service_account_path):
        print(f"Error: {service_account_path} not found.")
        return

    cred = credentials.Certificate(service_account_path)
    try:
        firebase_admin.initialize_app(cred, {
            'storageBucket': bucket_name
        })
    except ValueError:
        pass # Already initialized

    bucket = storage.bucket()
    blobs = bucket.list_blobs()

    print("Files in Firebase Storage:")
    for blob in blobs:
        print(f"- {blob.name} (Public URL: {blob.public_url})")

if __name__ == "__main__":
    verify_storage()
