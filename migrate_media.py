import os
import firebase_admin
from firebase_admin import credentials, storage

def upload_media():
    service_account_path = "firebase-service-account.json"
    media_dir = "media"
    bucket_name = "umeed-f2657.appspot.com" # Alternative default

    if not os.path.exists(service_account_path):
        print(f"Error: {service_account_path} not found.")
        return

    # Initialize firebase admin
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': bucket_name
    })

    bucket = storage.bucket()

    for root, dirs, files in os.walk(media_dir):
        for file in files:
            local_path = os.path.join(root, file)
            # Relative path from the media directory
            blob_path = os.path.relpath(local_path, media_dir).replace('\\', '/')
            blob = bucket.blob(blob_path)
            
            print(f"Uploading {local_path} to {blob_path}...")
            try:
                blob.upload_from_filename(local_path)
                # Make public
                blob.make_public()
                print(f"Successfully uploaded {blob_path}")
            except Exception as e:
                print(f"Failed to upload {blob_path}: {e}")

if __name__ == "__main__":
    upload_media()
