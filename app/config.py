import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    mongo_uri: str = os.getenv(
        "MONGO_URI",
        "mongodb://127.0.0.1:27017"
    )

    mongo_db: str = os.getenv(
        "MONGO_DB",
        "shopeasy"
    )

    session_secret: str = os.getenv(
        "SESSION_SECRET",
        "change-this-secret-key"
    )


settings = Settings()