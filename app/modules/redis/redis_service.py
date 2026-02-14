from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB


redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
