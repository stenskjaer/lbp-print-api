import json
import os
import subprocess

from flask import Flask, request, jsonify

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config

from processor import handle_job
from utils import setup_logger

# App version
__VERSION__ = subprocess.check_output("git describe --tags", shell=True).decode()

app = Flask(__name__, instance_path=os.getcwd())

logger = setup_logger("print_api")


@app.route("/api/v1/resource")
def process_resource():
    resource_id = request.args.get("id")
    resource_url = request.args.get("url")
    if not resource_id and not resource_url:
        error_message = {
            "error": "One of the parameters 'id' and 'url' must be given. 'id' must container an SCTA resource id, e.g. scta.info/resource/lectio1. 'url' must contain an http reference to an XML file, e.g. https://raw.githubusercontent.com/scta-texts/da-49/master/da-49-l1q1/da-49-l1q1.xml"
        }
        return jsonify(error_message)
    elif resource_id and resource_url:
        error_message = {
            "error": "One of the parameters 'id' and 'url' must be given, but not both."
        }
        return jsonify(error_message)

    if resource_id:
        resource_value = resource_id
        resource_type = "scta"
    else:
        resource_value = resource_url
        resource_type = "url"

    response = handle_job(resource_value, resource_type)

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
