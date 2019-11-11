import logging
import json
import os
import subprocess

from logging.config import dictConfig
from flask import Flask, request, make_response, jsonify
from flask.logging import default_handler
from flask import send_from_directory

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config

from processor import handle_job

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "test.log",
                "maxBytes": 5000000,
                "backupCount": 5,
            }
        },
        "root": {"level": logging.DEBUG, "handlers": ["default"]},
    }
)

# App version
#__VERSION__ = subprocess.check_output("git describe --tags", shell=True).decode()

app = Flask(__name__, instance_path=os.getcwd())

logger = logging.getLogger()
logger.addHandler(default_handler)


@app.route("/api/v1/resource")
def process_resource():
    logger.debug(f"Received request with args: {request.args}")
    resource_id = request.args.get("id")
    resource_url = request.args.get("url")
    if not resource_id and not resource_url:
        error_message = {
            "error": "One of the parameters 'id' and 'url' must be given. 'id' must container an SCTA resource id, e.g. scta.info/resource/lectio1. 'url' must contain an http reference to an XML file"
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
        trans = lbp_print.RemoteResource(resource_id)
    else:
        resource_value = resource_url
        resource_type = "url"
        trans = lbp_print.UrlResource(resource_url)

    cache = lbp_print.Cache("./cache")
    digest = trans.create_hash()
    if cache.contains(digest + ".pdf"):
        response = {"Status": "Finished", "url": digest + ".pdf"}
    else:
        response = handle_job(resource_value, resource_type)
        #response = handle_job(trans)
    #response = handle_job(resource_value, resource_type)
    #return jsonify(response)

    resp = make_response(jsonify(response),200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/api/v1/cache/<hashwithextension>", methods=['GET'])
def return_cache(hashwithextension):
    return send_from_directory("cache", hashwithextension)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
