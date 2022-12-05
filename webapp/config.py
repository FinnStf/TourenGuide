import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY_TOURGUIDE", "sdrfghstrzh35w32qrfqw2t2q")
    UPLOAD_EXTENSIONS = ['.csv']
    MONGODB_SETTINGS = {
        "db": "tourguideDB",
        "host": "localhost",
        "port": 27017
    }
