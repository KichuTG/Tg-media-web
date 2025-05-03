import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Configuration
    BOT_USERNAME = os.getenv("BOT_USERNAME", "@TGNETFLIX1BOT")
    
    # Database Configuration
    DATABASE_URI = os.getenv("DATABASE_URI", "mongodb+srv://jiosaavn:jiosaavn@cluster0.ouhhe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "PIRO")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "FILES")
    
    # Search Configuration
    USE_CAPTION_FILTER = bool(os.getenv("USE_CAPTION_FILTER", True))
    MAX_B_TN = os.getenv("MAX_B_TN", 50)  # Maximum buttons per page
