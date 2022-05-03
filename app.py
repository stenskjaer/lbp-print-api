import logging
import json
import os
import subprocess

import hashlib

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

@app.route("/")
def send_index():
    return "Welcome to the Lbp Print API; See <a href='http://localhost:5000/api/v1/docs/'>Documentation</a>"


@app.route("/api/v1/resource")
def process_resource():
    logger.debug(f"Received request with args: {request.args}")
    resource_id = request.args.get("id")
    resource_url = request.args.get("url")
    annolist = request.args.get("annolist")
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
    elif (annolist == "true"):
        resource_value = resource_url
        resource_type = "annolist"
        trans = resource_url
    else:
        resource_value = resource_url
        resource_type = "url"
        trans = lbp_print.UrlResource(resource_url)

    cache = lbp_print.Cache("./cache")

    digest = "unknown"
    if resource_type != "annolist":
        digest = trans.create_hash()

    #if cache.contains(digest + ".pdf" and resource_type != "annolist"):
     #   response = {"Status": "Finished", "url": digest + ".pdf"}
    #else:
    response = handle_job(resource_value, resource_type)
    #response = handle_job(trans)
    #response = handle_job(resource_value, resource_type)
    #return jsonify(response)

    resp = make_response(jsonify(response),200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/api/v1/annolist", methods=['POST'])
def process_post_resource():

    postdata = str(request.get_data().decode('utf-8'))
    datahash = hashlib.sha256(postdata.encode('utf-8')).hexdigest()
    resource_url = os.path.join("cache", datahash + '.json')

    with open(resource_url, mode='w', encoding='utf-8') as f:
        f.write(postdata)

    resource_value = resource_url
    resource_type = "annolist"
    trans = resource_url

    
    response = handle_job(resource_value, resource_type)

    resp = make_response(jsonify(response),200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    
    
    return resp
    

@app.route("/api/v1/cache/<hashwithextension>", methods=['GET'])
def return_cache(hashwithextension):
    return send_from_directory("cache", hashwithextension)

@app.route('/api/v1/docs/', defaults={'path': None})
@app.route("/api/v1/docs/<path:path>", methods=['GET'])
def send_docs(path):
    path = path if path else "index.html"
    return send_from_directory('static/docs', path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
