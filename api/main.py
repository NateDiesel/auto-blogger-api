import os
import sys
import requests
import logging
import sqlite3
import uuid
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, Depends, Query
from fastapi.security import APIKeyHeader
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import asyncio as aioredis
from pydantic import BaseModel
import openai
from datetime import datetime, timedelta
from typing import List

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load API keys
GUMROAD_PRODUCT_ID = os.getenv("GUMROAD_PRODUCT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

if not GUMROAD_PRODUCT_ID or not OPENAI_API_KEY or not ADMIN_API_KEY:
    raise ValueError("Missing API keys in .env file")

# OpenAI Client
openai_client = openai.OpenAI()

# FastAPI App
app = FastAPI(title="AI Auto-Blogger SaaS API", version="2.2")
APIKey = APIKeyHeader(name="X-API-Key", auto_error=True)

# Database Connection
def execute_db_query(query, params=(), fetchone=False, fetchall=False):
    """Executes a SQLite query safely."""
    with sqlite3.connect("api_keys.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()

# Ensure the correct database schema is set
execute_db_query('''
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    user_type TEXT CHECK(user_type IN ('trial', 'paid')) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  
    usage_count INTEGER DEFAULT 0
)
''')

# Fix missing column (if schema was incomplete)
try:
    execute_db_query("SELECT usage_count FROM api_keys LIMIT 1")
except sqlite3.OperationalError:
    execute_db_query("ALTER TABLE api_keys ADD COLUMN usage_count INTEGER DEFAULT 0")

# Redis Rate Limiting
@app.on_event("startup")
async def startup():
    try:
        app.state.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        await FastAPILimiter.init(app.state.redis)
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        app.state.redis = None  # Prevents crashes if Redis is down

@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()

# API Key Validation
def validate_api_key(api_key: str = Security(APIKey)):
    logging.info(f"Received API Key: {api_key}")

    if api_key == ADMIN_API_KEY:
        logging.info("Admin key recognized!")
        return "admin"

    db_result = execute_db_query(
        "SELECT user_type, usage_count, created_at FROM api_keys WHERE key = ?", 
        (api_key,), fetchone=True
    )

    if db_result:
        user_type, usage_count, created_at_str = db_result
        logging.info(f"User Type: {user_type}, Usage Count: {usage_count}, Created At: {created_at_str}")

        # Convert created_at to datetime object
        try:
            created_date = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            created_date = datetime.now()  # Fallback if format is incorrect

        expiration_date = created_date + timedelta(days=7)

        if user_type == "trial":
            if datetime.now() > expiration_date:
                logging.warning("Trial API key expired.")
                raise HTTPException(status_code=403, detail="Trial period expired")

            if usage_count >= 10:
                logging.warning("Trial API request limit reached.")
                raise HTTPException(status_code=403, detail="Trial request limit reached")

            # Increment usage count for trial users
            execute_db_query("UPDATE api_keys SET usage_count = usage_count + 1 WHERE key = ?", (api_key,))

        return user_type

    logging.warning("Invalid API Key Attempt")
    raise HTTPException(status_code=403, detail="Invalid API Key")

# Models
class BlogRequest(BaseModel):
    topic: str
    style: str
    tone: str
    word_count: int
    seo_keywords: List[str]

# API Key Generation Endpoint
@app.post("/generate-api-key")
def generate_api_key(user_type: str = Query(..., regex="^(trial|paid)$"), api_key: str = Security(APIKey)):
    if api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    new_key = str(uuid.uuid4())
    execute_db_query("INSERT INTO api_keys (key, user_type) VALUES (?, ?)", (new_key, user_type))

    return {"api_key": new_key, "user_type": user_type}

# Generate Blog Endpoint with SEO Optimization
@app.post("/generate-blog", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def generate_blog(request: BlogRequest, api_key: str = Security(APIKey)):
    user_type = validate_api_key(api_key)

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Write a {request.word_count}-word blog post about {request.topic} in a {request.style} style with a {request.tone} tone. Include the following SEO keywords naturally: {', '.join(request.seo_keywords)}."}
            ]
        )
        return {"status": "success", "blog_post": response.choices[0].message.content}

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail="OpenAI API error. Please try again later.")

# Health Check
@app.get("/health")
def health_check():
    return {"status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
