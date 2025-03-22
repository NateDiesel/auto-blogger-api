import requests
import openai
import json
import logging
from datetime import datetime
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException

# Configure logging
logging.basicConfig(filename="auto_blogger.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration
CONFIG_FILE = "config.json"
try:
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
except FileNotFoundError:
    logging.error("CONFIG FILE MISSING: Please create a config.json file.")
    exit()

# Gumroad API Key Validation
GUMROAD_PRODUCT_ID = "YOUR_GUMROAD_PRODUCT_ID"
GUMROAD_API_URL = "https://api.gumroad.com/v2/licenses/verify"

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def validate_gumroad_key(api_key: str):
    """Verify Gumroad License Key before allowing API access."""
    response = requests.post(GUMROAD_API_URL, data={
        "product_id": GUMROAD_PRODUCT_ID,
        "license_key": api_key
    })
    result = response.json()
    
    if not result.get("success"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    return api_key

# OpenAI API Key
OPENAI_API_KEY = config.get("openai_api_key")
if not OPENAI_API_KEY:
    logging.error("Missing OpenAI API Key in config.json")
    exit()
openai.api_key = OPENAI_API_KEY

# SEO API Settings
SEO_API_URL = "YOUR_SEO_API_ENDPOINT"

def generate_blog_post(topic, api_key):
    """Generate an AI-written blog post with OpenAI."""
    prompt = f"""
    Write a detailed, SEO-optimized blog post about {topic}. 
    - Include engaging headings, bullet points, and structured content.
    - Add a short SEO meta description.
    - Use HTML formatting (bold, lists, headers).
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert blog writer."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response["choices"][0]["message"]["content"].strip()
        
        # Send to SEO API for Optimization
        optimized_content = optimize_content_with_seo_api(content, api_key)
        return optimized_content
    except Exception as e:
        logging.error(f"OpenAI API Failed: {e}")
        return None

def optimize_content_with_seo_api(content, api_key):
    """Send the blog post to SEO Optimizer API for enhancements."""
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    response = requests.post(SEO_API_URL, json={"content": content}, headers=headers)
    if response.status_code == 200:
        return response.json().get("optimized_content", content)
    else:
        logging.error("SEO API Optimization Failed")
        return content

if __name__ == "__main__":
    user_api_key = input("Enter your Gumroad API Key: ")
    try:
        validate_gumroad_key(user_api_key)
        topic = input("Enter blog topic: ")
        final_post = generate_blog_post(topic, user_api_key)
        print("\nGenerated Blog Post:\n", final_post)
    except HTTPException as e:
        print("Access Denied: Invalid API Key")
 