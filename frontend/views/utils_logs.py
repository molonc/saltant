"""Contains helpers for getting task instance logs."""

import os
from django.conf import settings
import boto3
from azure.storage.blob import ContainerClient


def get_azure_logs_for_task_instance(job_uuid):
    if (
        not os.environ["AZURE_STORAGE_ACCOUNT_NAME"]
        or not os.environ["AZURE_STORAGE_ACCOUNT_KEY"]
        or not os.environ["AZURE_LOGS_CONTAINER_NAME"]
    ):
        return {}

    container_client = ContainerClient(account_url="https://"+os.environ["AZURE_STORAGE_ACCOUNT_NAME"]+".blob.core.windows.net/",
                                       container_name=os.environ["AZURE_LOGS_CONTAINER_NAME"], credential=os.environ["AZURE_STORAGE_ACCOUNT_KEY"])
    log_files = container_client.list_blobs(name_starts_with=job_uuid)
    log_files_dict = {}
    for log_file in log_files:
        # Extract the file name and text
        file_name = log_file.name.split("/")[-1:][0]
        file_last_modified = log_file.last_modified
        blob_client = container_client.get_blob_client(blob=log_file)
        download_stream = blob_client.download_blob(encoding="utf-8")
        file_text = download_stream.readall()
        # Add in this log file to our output
        sub_dict = {"last_modified": file_last_modified, "text": file_text}
        log_files_dict[file_name] = sub_dict

    return log_files_dict


def get_azure_logs_for_executable_task_instance(job_uuid):
    # Call the base function
    these_logs = get_azure_logs_for_task_instance(job_uuid)

    # Get out if these logs don't exist
    if not these_logs:
        return these_logs

    # Update the key names
    these_logs["stdout"] = these_logs.pop(job_uuid + "-" + "stdout.txt")
    these_logs["stderr"] = these_logs.pop(job_uuid + "-" + "stderr.txt")

    return these_logs
