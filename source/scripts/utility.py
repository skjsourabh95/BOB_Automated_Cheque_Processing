import os
from azure.storage.blob import BlobServiceClient


def upload_blob(local_file_path,container_name,connect_str):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # Create a blob client using the local file name as the name for the blob
    filename = local_file_path.split(os.sep)[-1]
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    print("\nUploading to Azure Storage as blob")
    # Upload the created file
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data,overwrite=True)
    return f"https://bobdocs.blob.core.windows.net/bob-run-docs/{filename}"

def check_signature_from_azure(identified_labels):
    for key,value in identified_labels.items():
        if type(value) == dict:
            if value['value'] == "signed" and value['confidence'] > 0.50:
                sign_present = True
            if "signature" in key and value['value'] == "unsigned":
                sign_present = False
    return sign_present