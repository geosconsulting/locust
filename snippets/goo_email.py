from google.cloud import storage


def get_service_account():
    """Get the service account email"""
    storage_client = storage.Client()

    email = storage_client.get_service_account_email()
    print(
        "The GCS service account for project {} is: {} ".format(
            storage_client.project, email
        )
    )
