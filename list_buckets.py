from google.cloud import storage

def list_buckets():
    service_account_path = "firebase-service-account.json"
    client = storage.Client.from_service_account_json(service_account_path)
    buckets = client.list_buckets()
    print("Available buckets:")
    for bucket in buckets:
        print(f"- {bucket.name}")

if __name__ == "__main__":
    list_buckets()
