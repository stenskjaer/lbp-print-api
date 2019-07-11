import logging

import lbp_print.core as lbp_print
import lbp_print.config as lbp_config
lbp_config.cache_dir = "cache"

logger = logging.getLogger("rq.worker")

def convert_resource(id: str) -> str:
    logger.error(f"Processing remote resource {id}.")
    trans = lbp_print.RemoteTranscription(id)

    filename = lbp_print.Tex(trans).process(output_format="tex")
    return filename
