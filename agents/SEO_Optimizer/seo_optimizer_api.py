import uvicorn
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import textstat
import json
import os
from dotenv import load_dotenv
import re
import random
from bs4 import BeautifulSoup
import openai

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define API Key Authentication
API_KEYS = {
    "free_user": os.getenv("FREE_API_KEY", "free-api-key"),
    "paid_user": os.getenv("PAID_API_KEY", "paid-api-key")
}

# Define FastAPI instance
app = FastAPI(title="SEO Optimizer API", version="1.2")

class SEORequest(BaseModel):
    content: str
    optimization_mode: str = "balanced"  # Options: aggressive, balanced, light

def calculate_keyword_density(content):
    words = content.lower().split()
    total_words = len(words)
    word_freq = {}

    for word in words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1

    keyword_density = {word: round((freq / total_words) * 100, 2) for word, freq in word_freq.items()}
    return keyword_density

def analyze_readability(content):
    return {
        "readability_score": textstat.flesch_reading_ease(content),
        "readability_level": textstat.text_standard(content)
    }

def generate_schema(content):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "articleBody": content[:200] + "...",
        "author": "AI SEO Optimizer",
        "publisher": "Your Website"
    }

def optimize_content(content, mode):
    replacements = {
        "SEO": "Search Engine Optimization",
        "content": "digital content",
        "marketing": "digital marketing strategy"
    }
    if mode == "aggressive":
        for word, replacement in replacements.items():
            content = content.replace(word, replacement)
    return content

def generate_meta_tags(content):
    meta_description = content[:150] + "..."
    title = content.split(".")[0] if "." in content else "Optimized SEO Title"
    return {
        "meta_title": title,
        "meta_description": meta_description
    }

def extract_links(content):
    soup = BeautifulSoup(content, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return links if links else ["No internal links detected."]

def generate_faq(content):
    prompt = f"Generate 3 SEO-friendly FAQ questions and answers based on the following content:\n{content}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an SEO expert generating FAQs."},
                  {"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )
    return response["choices"][0]["message"]["content"]

def ai_seo_suggestions(content):
    prompt = f"Analyze the following content for SEO improvements and suggest optimizations:\n{content}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an SEO expert providing detailed content analysis."},
                  {"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )
    return response["choices"][0]["message"]["content"]

@app.post("/optimize/")
def optimize_seo(seo_request: SEORequest, api_key: str = Header(None)):
    if api_key not in API_KEYS.values():
        raise HTTPException(status_code=403, detail="Invalid API Key")

    keyword_density = calculate_keyword_density(seo_request.content)
    readability = analyze_readability(seo_request.content)
    schema_markup = generate_schema(seo_request.content)
    optimized_content = optimize_content(seo_request.content, seo_request.optimization_mode)
    meta_tags = generate_meta_tags(seo_request.content)
    internal_links = extract_links(seo_request.content)
    faq_data = generate_faq(seo_request.content)
    seo_suggestions = ai_seo_suggestions(seo_request.content)

    return {
        "before": {
            "content": seo_request.content,
            "seo_score": round(readability["readability_score"]),
            "keyword_density": keyword_density
        },
        "after": {
            "content": optimized_content,
            "seo_score": round(readability["readability_score"]) + 10,
            "keyword_density": keyword_density
        },
        "meta_tags": meta_tags,
        "internal_links": internal_links,
        "schema_markup": schema_markup,
        "faq": faq_data,
        "seo_suggestions": seo_suggestions,
        "suggestions": [
            "Consider using more keywords naturally within the content.",
            "Break longer paragraphs into shorter, readable chunks."
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
