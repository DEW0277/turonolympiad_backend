import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()


# Additional settings can be added here, such as database connections, logging configurations, etc.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


# Password context with Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# REDIS settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))


# telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_HOST_URL = os.getenv("WEBHOOK_HOST_URL")