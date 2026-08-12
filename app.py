import os
from io import BytesIO

import boto3
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

# =========================
# AWS S3 configuration
# =========================

AWS_PROFILE = os.getenv("AWS_PROFILE")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# If AWS_PROFILE exists, use it locally.
# In Docker/Kubernetes, no profile is needed;
# boto3 will automatically use AWS environment credentials.
if AWS_PROFILE:
    aws_session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )
else:
    aws_session = boto3.Session(
        region_name=AWS_REGION
    )

s3 = aws_session.client("s3")


# =========================
# Azure Blob Storage
# =========================

AZURE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

AZURE_CONTAINER_NAME = os.getenv(
    "AZURE_CONTAINER_NAME",
    "uploads"
)

azure_blob_service = BlobServiceClient.from_connection_string(
    AZURE_CONNECTION_STRING
)


# =========================
# Routes
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    file = request.files.get("file")

    if not file or file.filename == "":
        return "No file selected", 400

    filename = secure_filename(file.filename)

    if not filename:
        return "Invalid filename", 400

    # Read the uploaded file once.
    # The same data will be sent to both cloud providers.
    file_data = file.read()

    # =========================
    # Upload to AWS S3
    # =========================

    s3.upload_fileobj(
        BytesIO(file_data),
        S3_BUCKET_NAME,
        filename
    )

    # =========================
    # Upload to Azure Blob Storage
    # =========================

    container_client = azure_blob_service.get_container_client(
        AZURE_CONTAINER_NAME
    )

    blob_client = container_client.get_blob_client(
        filename
    )

    blob_client.upload_blob(
        BytesIO(file_data),
        overwrite=True
    )

    return (
        f"File '{filename}' uploaded successfully "
        "to AWS S3 and Azure Blob Storage!"
    )


# =========================
# Run application
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )