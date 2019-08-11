import json
import logging
import os
import subprocess
from logging import handlers

from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config

from processor import convert_resource

# App version
__VERSION__ = subprocess.check_output("git describe --tags", shell=True).decode()

app = Flask(__name__, instance_path=os.getcwd())

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler = handlers.RotatingFileHandler(
    "logs/service.log", maxBytes=1024 * 1000, backupCount=5
)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

q = Queue(connection=Redis())


def start_job(resource_value: str, resource_type: str):
    return q.enqueue(
        convert_resource,
        resource_value,
        resource_type,
        job_id=resource_value,
        job_timeout="1h",
        result_ttl=30,
    )


def handle_job(resource_id: str, resource_type: str) -> dict:
    try:
        job = Job.fetch(resource_id, connection=Redis())
    except NoSuchJobError:
        job = start_job(resource_id, resource_type)
        return {"Status": "Started"}

    if job.result:
        response = {"Status": "Finished", "url": job.result}
    elif job.is_failed:
        response = {
            "Status": "Failed. Resubmit to retry.",
            "error": job.meta["progress"],
        }
        job.delete()
    else:
        response = {"Status": "Working"}
    return response


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
