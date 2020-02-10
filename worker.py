#!/usr/bin/env python
import sys
import os
from redis import Redis
from rq import Connection, Worker


def start_worker(queues: list = ["default"]):
    redis_endpoint = os.getenv("REDIS_ENDPOINT", "localhost")
    with Connection():
        w = Worker(queues, connection=Redis(host=redis_endpoint))
        w.work()


if __name__ == "__main__":
    qs = sys.argv[1:] or ["default"]
    start_worker(qs)
