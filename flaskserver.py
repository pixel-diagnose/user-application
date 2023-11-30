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
            print("saved file")
            # Get only embedding from uploaded picture here
            embeddings_from_upload = do_inference(
                "img2vec50", os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
            # Query QDRAN
            # for diagnose is diagnose:
            #   Do request
            search_results = get_similar_embeddings(
                search_vector=embeddings_from_upload,
                collection_name="resnet50_imagenet_embeddings",
                num_results=10,
                filter_diagnose=None,
                filter_image_type=None,
            )
            # Return JSON from QDRANT
            print(search_results)
            results_with_url = generate_signed_url(search_results)
            print("-------with url--------")
            print(results_with_url)

            encoded_string = ""
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            data = {"thing": results_with_url, "image_data": encoded_string}

            return jsonify(data)


@app.route("/")
def frontend():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
