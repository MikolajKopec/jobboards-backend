from os import getenv
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = getenv("SECRET_KEY", "_%R@J_TNQ_W___W_W")
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URL").replace(
        "postgres://", "postgresql://"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = getenv("GOOGLE_REDIRECT_URI")
    GOOGLE_ACCESS_TOKEN_URL = getenv("GOOGLE_ACCESS_TOKEN_URL")
    GOOGLE_API_BASE_URL = getenv("GOOGLE_API_BASE_URL")
    GOOGLE_AUTHORIZE_URL = getenv("GOOGLE_AUTHORIZE_URL")
    FRONTEND_URL = getenv("FRONTEND_URL")
