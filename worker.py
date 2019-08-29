#!/usr/bin/env python
import sys

from redis import Redis
from rq import Connection, Worker


def start_worker(queues: list = ["default"]):
    with Connection():
        w = Worker(queues, connection=Redis(host="redis"))
        w.work()


if __name__ == "__main__":
    qs = sys.argv[1:] or ["default"]
    start_worker(qs)
