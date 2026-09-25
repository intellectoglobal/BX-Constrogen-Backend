import redis
from django.conf import settings


class RedisHelper:
    def __init__(self):
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.user = settings.REDIS_USER
        self.pwd = settings.REDIS_PWD

    def connect_to_redis(self):
        try:
            db = redis.Redis(
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.pwd,
                decode_responses=True
            )
            if db.ping():
                return {'Connected': True, 'Connection': db}
        except Exception as e:
            return {'Connected': False, 'Connection': None, 'Error': str(e)}

    def store_otp(self, email, otp, ttl: int = 300):
        conn_result = self.connect_to_redis()
        if not conn_result['Connected']:
            return False
        try:
            redis_connection = conn_result['Connection']
            key = f"otp:{email}"
            redis_connection.set(key, otp, ex=ttl)
            return True
        except Exception:
            return False

    def verify_otp(self, email, otp):
        conn_result = self.connect_to_redis()
        if not conn_result['Connected']:
            return False, 'Error while connecting to Redis'
        try:
            redis_connection = conn_result['Connection']
            key = f"otp:{email}"
            stored_otp = redis_connection.get(key)

            if stored_otp is None:
                return False, 'OTP expired or not found'

            if int(stored_otp) == otp:
                redis_connection.delete(key)
                return True, 'OTP verified successfully'
            else:
                return False, 'Invalid OTP'
        except Exception as e:
            return False, f'Error occurred: {str(e)}'
