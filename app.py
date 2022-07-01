#!/usr/bin/env python

from os import getenv
from dotenv import load_dotenv
from autotagger import Autotagger
from base64 import b64encode
from fastai.vision.core import PILImage
from flask import Flask, request, render_template, jsonify, abort
from werkzeug.exceptions import HTTPException
import torch

load_dotenv()
model_path = getenv("MODEL_PATH", "models/model.pth")
autotagger = Autotagger(model_path)

# This is necessary for Gunicorn to work with multiple workers and preloading enabled.
torch.set_num_threads(1)
#autotagger.learn.model.eval()
#autotagger.learn.model.share_memory()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["JSON_PRETTYPRINT_REGULAR"] = True

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/evaluate", methods=["POST"])
def evaluate():
    files = request.files.getlist("file")
    threshold = float(request.values.get("threshold", 0.1))
    output = request.values.get("format", "html")
    limit = int(request.values.get("limit", 50))

    images = [PILImage.create(file) for file in files]
    predictions = autotagger.predict(images, threshold=threshold, limit=limit)

    if output == "html":
        for file in files:
            file.seek(0)

        base64data = [b64encode(file.read()).decode() for file in files]
        return render_template("evaluate.html", predictions=zip(base64data, predictions))
    elif output == "json":
        predictions = [{ "filename": file.filename, "tags": tags } for file, tags in zip(files, predictions)]
        return jsonify(predictions)
    else:
        abort(400)

@app.errorhandler(HTTPException)
def handle_http_exception(exception):
    output = request.values.get("format", "html")

    if hasattr(exception, "original_exception"):
        error = exception.original_exception.__class__.__name__
        message = str(exception.original_exception)
    else:
        error = exception.__class__.__name__
        message = str(exception)

    if output == "html":
        return render_template("error.html", error=error, message=message)
    else:
        return jsonify({ "error": error, "message": message }), exception.code

if __name__ == "__main__":
    app.run(host="0.0.0.0")
