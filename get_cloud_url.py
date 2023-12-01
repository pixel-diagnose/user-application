from google.cloud import storage
from google.oauth2 import service_account

# Set the path to your private key file
private_key_path = "./google_service_credentials.json"

# Set the GCS bucket and object path
# bucket_name = "schwannoma-mc-rc"
# object_path = (
#    "tcia-test/1.3.6.1.4.1.14519.5.2.1.77766633296647526214282450446735028767/1-92.dcm"
# )


# Function to generate a signed URL
def generate_signed_url(search_results):
    for i in search_results.keys():
        search_res = search_results[i]
        # Load credentials from the private key file
        bucket_url = search_res["bucket_url"]
        bucket_name = bucket_url.split("/")[2]
        object_path = (
            "/".join(bucket_url.split("/")[3:])
            + "png/"
            + search_res["patient_id"]
            + "_"
            + search_res["image_type"]
            + "_sliced.png"
        )
        credentials = service_account.Credentials.from_service_account_file(
            private_key_path
        )
        client = storage.Client(credentials=credentials)

        bucket = client.bucket(bucket_name)
        blob = bucket.blob(object_path)

        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=3600,  # URL expires in 60 minutes (3600 seconds)
            method="GET",
        )
        search_results[i]["signed_url"] = signed_url
    return search_results
