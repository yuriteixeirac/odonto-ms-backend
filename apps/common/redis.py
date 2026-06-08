import os

import redis

redis_cli = redis.Redis(
    host=os.getenv("REDIS_HOST") or "localhost",
    port=int(os.getenv("REDIS_PORT") or 6379),
    decode_responses=True,
)
