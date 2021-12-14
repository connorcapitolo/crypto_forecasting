import os
from google.cloud import storage


gcp_project = os.environ["GCP_PROJECT"]
bucket_name = os.environ["GCS_BUCKET"]
persistent_folder = "/app"


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""

    # uses the module storage_client
    # this implicitly calls to "secrets/bucket-reader.json" from the GOOGLE_APPLICATION_CREDENTIALS
    storage_client = storage.Client(project=gcp_project)

    # open the bucket
    bucket = storage_client.bucket(bucket_name)
    # looks inside the bucket
    blob = bucket.blob(source_blob_name)
    # download specific file
    blob.download_to_filename(destination_file_name)

print(bucket_name)
print(gcp_project)

# Test access
download_file = "test-bucket-access.txt"
download_blob(bucket_name, download_file,
              os.path.join(persistent_folder, download_file))
