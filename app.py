import os

from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return "No file was selected."

    file = request.files["file"]

    if file.filename == "":
        return "No file was selected."

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

    return f"File '{file.filename}' uploaded successfully!"


if __name__ == "__main__":
    app.run(debug=True)