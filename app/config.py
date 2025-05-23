import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.API_ENDPOINT = os.getenv("API_ENDPOINT", "https://jsonplaceholder.typicode.com")
        self.API_KEY = os.getenv("API_KEY", "")
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10)) # seconds
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
        self.RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", 1.5)) # seconds
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://kateb7566:123456@postgres:5432/kateb_pipeline")
        
        
settings = Settings()