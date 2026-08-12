import os

import boto3
from dotenv import load_dotenv
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_PROFILE = os.getenv("AWS_PROFILE", "cloud-project")

session = boto3.Session(
    profile_name=AWS_PROFILE,
    region_name=AWS_REGION
)

s3 = session.client("s3")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return "No file was selected.", 400

    file = request.files["file"]

    if file.filename == "":
        return "No file was selected.", 400

    filename = secure_filename(file.filename)

    s3.upload_fileobj(
        file,
        S3_BUCKET_NAME,
        filename
    )

    return f"File '{filename}' uploaded successfully to AWS S3!"


if __name__ == "__main__":
    app.run(debug=True)