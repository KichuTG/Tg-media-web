import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
import re
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Telegram Media Search API")

# Create required directories if they don't exist
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Mount static files if directory exists
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Database configuration
DATABASE_URI = os.getenv("MONGODB_URI", "mongodb+srv://jiosaavn:jiosaavn@cluster0.ouhhe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.getenv("DATABASE_NAME", "PIRO")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "FILES")
BOT_USERNAME = os.getenv("BOT_USERNAME", "TGNETFLIX1BOT")

# Initialize MongoDB client
try:
    client = AsyncIOMotorClient(DATABASE_URI)
    db = client[DATABASE_NAME]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB connection closed")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main search page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "bot_username": BOT_USERNAME
        }
    )

@app.get("/api/search")
async def search_files(
    query: Optional[str] = None,
    file_type: Optional[str] = None,
    max_results: int = 50,
    offset: int = 0
):
    """
    Search endpoint for media files
    Returns:
        - List of matching files
        - Next offset
        - Total results count
    """
    if not query or query.strip() == '':
        return {
            "results": [],
            "next_offset": "",
            "total": 0
        }

    try:
        # Clean and prepare search query
        query = query.strip()
        query_words = query.split(' ')
        
        # Build regex pattern similar to original Python implementation
        if len(query_words) == 1:
            raw_pattern = r'(\b|[\.\+\-_])' + query_words[0] + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

        regex = re.compile(raw_pattern, flags=re.IGNORECASE)

        # Build filter
        search_filter = {
            "$or": [
                {"file_name": {"$regex": regex}},
                {"caption": {"$regex": regex}}
            ]
        }

        if file_type:
            search_filter["file_type"] = file_type

        # Get total count
        total = await db[COLLECTION_NAME].count_documents(search_filter)

        # Calculate next offset
        next_offset = offset + max_results
        if next_offset >= total:
            next_offset = ""

        # Execute query
        cursor = db[COLLECTION_NAME].find(search_filter)
        cursor.sort("$natural", -1).skip(offset).limit(max_results)
        
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["telegram_link"] = f"https://t.me/{BOT_USERNAME}?start={doc['_id']}"
            results.append(doc)

        return {
            "results": results,
            "next_offset": next_offset,
            "total": total
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Verify database connection
        await db.command("ping")
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
