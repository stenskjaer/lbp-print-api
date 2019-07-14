import logging
from logging import handlers

from rq import get_current_job

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config

lbp_config.cache_dir = "cache"

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


def update_status(message, job):
    job.meta["progress"] = message
    job.save_meta()
    logger.info(message)


def convert_resource(id: str) -> str:
    job = get_current_job()
    update_status(f"Processing remote resource {id}.", job)

    trans = lbp_print.RemoteTranscription(id)
    update_status(f"Identified and downloaded resource {id}.", job)

    update_status(f"Converting resource to pdf.", job)
    try:
        filename = lbp_print.Tex(trans).process(output_format="pdf")
    except:
        raise

    update_status(f"Successfully converted resource {id} to pdf.", job)
    return filename
