import json
import logging
import multiprocessing
import os
import subprocess

from logging import handlers

from flask import Flask, render_template, request
from flask import jsonify, make_response

from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config

lbp_config.cache_dir = "cache"

from forms import TranscriptionForm
from upload_file import UploadFile

# App version
__VERSION__ = subprocess.check_output("git describe --tags", shell=True).decode()

app = Flask(__name__, instance_path=os.getcwd())
app.config.from_object(__name__)  # load config from this file
app.config.update(
    dict(
        SECRET_KEY="development key",
        USERNAME="admin",
        PASSWORD="default",
        UPLOAD_FOLDER=os.path.join(app.instance_path, "upload"),
    )
)
socketio = SocketIO(app)

root = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARN)
file_handler = handlers.RotatingFileHandler(
    "logs/service.log", maxBytes=1024 * 1000, backupCount=5
)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
root.addHandler(stream_handler)
root.addHandler(file_handler)


@app.route("/compile")
def service():
    parameters = {
        "scta_id": request.args.get("id"),
        "tex_or_pdf": request.args.get("output", "tex"),
    }

    try:

        logging.info("Looking for remote resource.")
        trans = lbp_print.RemoteTranscription(parameters["scta_id"])

        if parameters["tex_or_pdf"] == "tex":
            format = "tex"
        else:
            format = "pdf"

        logging.info("Using default XSLT conversion script.")
        res_file = lbp_print.Tex(
            trans, output_format=format, output_dir="static/output"
        ).process()

    except AttributeError:
        error_message = (
            "You gave the following parameters: %s. 'tex_or_pdf' must be either "
            "'tex' or 'pdf' (default is 'tex'). 'scta_id' must be a valid SCTA id"
            " (full url or id)." % format(parameters)
        )
        return make_response(jsonify({"error": error_message}), 404)
    return jsonify({"url": request.host + "/" + res_file})


@app.route("/")
def submit():
    form = TranscriptionForm()
    return render_template("index_form.html", form=form, version=__VERSION__)


if __name__ == "__main__":
    socketio.run(app, debug=True)
