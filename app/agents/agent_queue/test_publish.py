import redis
from ...core.config import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
r.publish("agents", "hello from test publisher")
print("Message sent!")