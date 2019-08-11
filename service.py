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


def start_job(resource_id):
    return q.enqueue(
        convert_resource,
        resource_id,
        job_id=resource_id,
        job_timeout="1h",
        result_ttl=30,
    )


@app.route("/api/v1/resource")
def service():
    resource_id = request.args.get("id")
    if not resource_id:
        error_message = {
            "error": "The parameter 'id' is requied. It must container an SCTA resource id, e.g. scta.info/resource/lectio1"
        }
        return jsonify(error_message)

    response = {"status": "failed", "progress": ""}

    try:
        job = Job.fetch(resource_id, connection=Redis())
        response["progress"] = job.meta["progress"]

        if job.result:
            response = {"status": "finished", "url": job.result}
        if job.is_failed:
            response["status"] = "failed"
            job.cancel()
            job.cleanup()
            job = start_job(resource_id)
        else:
            response["status"] = "working"
    except NoSuchJobError:
        job = start_job(resource_id)
        response["status"] = "started"

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
