import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in the .env file"
    )

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-development-secret",
)

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured in the .env file"
    )

JWT_ALGORITHM = "HS256"

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


TEACHER_REGISTRATION_KEY = os.getenv(
    "TEACHER_REGISTRATION_KEY",
)

if not TEACHER_REGISTRATION_KEY:
    raise RuntimeError(
        "TEACHER_REGISTRATION_KEY is not configured in the .env file"
    )
