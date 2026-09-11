import redis
from app.core.config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

r.set("test_key", "hello")
print(r.get("test_key"))  # should print 'hello'