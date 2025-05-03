from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from motor.motor_asyncio import AsyncIOMotorClient
import re

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Database connection
DATABASE_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "telegram_files")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "media_files")
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = client
    app.mongodb = db

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/search")
async def search_files(query: str = None):
    if not query or query.strip() == '':
        return []
    
    query_words = query.split(' ')
    regex_pattern = query_words[0]
    
    if len(query_words) == 1:
        regex_pattern = f"(\\b|[\\.\\+\\-_]){query_words[0]}(\\b|[\\.\\+\\-_])"
    else:
        regex_pattern = query_words.join('.*[\\s\\.\\+\\-_]')
    
    try:
        regex = re.compile(regex_pattern, re.IGNORECASE)
    except:
        return []
    
    cursor = db[COLLECTION_NAME].find({
        "$or": [
            {"file_name": {"$regex": regex}},
            {"caption": {"$regex": regex}}
        ]
    }).sort("$natural", -1).limit(50)
    
    results = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        results.append(document)
    
    return results
