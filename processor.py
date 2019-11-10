import logging

import urllib
from typing import Union

from redis import Redis
from rq import get_current_job, Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config
from lbp_print.exceptions import SaxonError

logger = logging.getLogger()
lbp_config.cache_dir = "cache"
redis_connection = Redis(host="localhost")
q = Queue(connection=redis_connection)


def check_for_existing_job(resource_value: str) -> Union[Job, bool]:
    """Checks whether a job is running with the given id. Return the job object if it 
    runs, otherwise False.
    """
    try:
        logger.debug(f"Checking for job with the id {resource_value}")
        return Job.fetch(resource_value, connection=redis_connection)
    except NoSuchJobError:
        logger.debug(f"No existing job with the id {resource_value}")
        return False


def job_status(job: Job) -> dict:
    status = job.meta["progress"]

    if job.result:
        response = {"Status": "Finished", "url": job.result}
        logger.debug(f"Job was finished. Result: " + job.result)
    elif job.is_failed:
        response = {"Status": "Failed. Resubmit to retry.", "error": status}
        logger.warn(f"Job failed." + status)
        job.delete()
    else:
        response = {"Status": status}
        logger.debug(f"Job running. Status: " + status)
    return response


def start_job(trans, resource_value) -> dict:
    logger.debug(f"No existing job. Starting one up ...")
    job = q.enqueue(
        convert_resource,
        trans,
        resource_value,
        job_id=resource_value,
        job_timeout="1h",
        result_ttl=30,
    )
    return {"Status": f"Processing {resource_value}"}


def update_status(message, job):
    job.meta["progress"] = message
    job.save_meta()
    logger.info(message)


def convert_resource(trans, resource_value) -> str:
    job = get_current_job()

    update_status(f"Converting {resource_value} to pdf.", job)
    try:
        filename = lbp_print.Tex(trans).process(output_format="pdf")
    except SaxonError as exc:
        update_status(str(exc), job)
        raise
    update_status(f"Successfully converted {resource_value} to pdf.", job)

    return filename
