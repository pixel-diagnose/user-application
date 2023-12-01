import os
from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    render_template,
    send_file,
    Response,
    jsonify,
)
import secrets
from werkzeug.utils import secure_filename
from inference import do_inference
from google.cloud import storage
from google.auth import compute_engine
from get_cloud_url import generate_signed_url
from qdrant_stuff import get_similar_embeddings
import json

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "dcm", "nii.gz"}


app = Flask(__name__)

app.secret_key = secrets.token_hex(16)  # Set a random secret key
app.config["STATIC_FOLDER"] = "static"  # Set the static folder
app.config["UPLOAD_FOLDER"] = "./uploads"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/inference", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        print("XXXXXXXXXXXXXXXXXXXXXXXX" + request.form["cancer_types"])
        for key, value in request.form.items():
            print(key, value)
        print("XXXXXXXXXXXXXXXXXXXXXXXX" + request.form["image_type"])
        print("XXXXXXXXXXXXXXXXXXXXXXXX" + request.form["number_of_results"])
        if "img" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["img"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            # Get only embedding from uploaded picture here
            embeddings_from_upload = do_inference(
                "img2vec50", os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
            # Query QDRANT
            num_qdrant_results = int(request.form["number_of_results"])
            requested_image_type = "".join(
                [
                    key
                    for key, value in json.loads(request.form["image_type"]).items()
                    if value == "true"
                ]
            )
            assert len(requested_image_type) == 1
            requested_diagnoses = [
                key.replace("Gliomas", "glioma")
                .replace("Meningiomas", "men")
                .replace(
                    "Metastasis", "met"
                )  # change because disgnoses are stored differnetly on QDRANT
                for key, value in json.loads(request.form["cancer_types"]).items()
                if value == "true"
            ]
            results = {
                diagnose: generate_signed_url(
                    get_similar_embeddings(
                        search_vector=embeddings_from_upload,
                        collection_name="resnet50_imagenet_embeddings",
                        num_results=num_qdrant_results,
                        filter_diagnose=[diagnose],
                        filter_image_type=requested_image_type,
                    )
                )
                for diagnose in requested_diagnoses
            }
            # Return JSON from QDRANT
            print("-------with url--------")
            print(results)

            return jsonify(results)


@app.route("/")
def frontend():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
