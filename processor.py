import logging

from redis import Redis
from rq import get_current_job, Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config
from lbp_print.exceptions import SaxonError

logger = logging.getLogger()

lbp_config.cache_dir = "cache"

q = Queue(connection=Redis())


def handle_job(resource_value: str, resource_type: str) -> dict:
    try:
        job = Job.fetch(resource_value, connection=Redis())
    except NoSuchJobError:
        job = q.enqueue(
            convert_resource,
            resource_value,
            resource_type,
            job_id=resource_value,
            job_timeout="1h",
            result_ttl=30,
        )
        return {"Status": f"Started processing {resource_value}"}

    if job.result:
        response = {"Status": "Finished", "url": job.result}
    elif job.is_failed:
        response = {
            "Status": "Failed. Resubmit to retry.",
            "error": job.meta["progress"],
        }
        job.delete()
    else:
        response = {"Status": job.meta["progress"]}
    return response


def update_status(message, job):
    job.meta["progress"] = message
    job.save_meta()
    logger.info(message)


def convert_resource(id: str, resource_type: str) -> str:
    job = get_current_job()
    update_status(f"Start processing {id}.", job)

    if resource_type == "scta":
        trans = lbp_print.RemoteResource(id)
    elif resource_type == "url":
        trans = lbp_print.UrlResource(id)
    else:
        raise ValueError(f"Trying to convert {id} of illegal type {resource_type}")
    update_status(f"Identified and downloaded {id}.", job)

    update_status(f"Converting {id} to pdf.", job)
    try:
        filename = lbp_print.Tex(trans).process(output_format="pdf")
    except SaxonError as exc:
        update_status(str(exc), job)
        raise
    update_status(f"Successfully converted {id} to pdf.", job)

    return filename
