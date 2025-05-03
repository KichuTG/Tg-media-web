import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Configuration
    BOT_USERNAME = os.getenv("BOT_USERNAME", "")
    
    # Database Configuration
    DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "telegram_files")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "media_files")
    
    # Search Configuration
    USE_CAPTION_FILTER = bool(os.getenv("USE_CAPTION_FILTER", True))
    MAX_B_TN = os.getenv("MAX_B_TN", 10)  # Maximum buttons per page
