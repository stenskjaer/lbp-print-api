#!/usr/bin/env python
import sys

from redis import Redis
from rq import Connection, Worker

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with Connection():
    qs = sys.argv[1:] or ["default"]

    w = Worker(qs, connection=Redis(host="redis"))
    w.work()
