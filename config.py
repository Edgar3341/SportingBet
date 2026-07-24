from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

BASE_URL = os.getenv("BASE_URL")
USER_ID = os.getenv("user_id") or os.getenv("candidate")
USER_ID_HEADER = "x-user-id"
DEFAULT_TIMEOUT = 15
