#Readme
# AI Auto-Blogger

## 🚀 Overview
The AI Auto-Blogger is an automation tool that generates and publishes SEO-optimized blog posts using OpenAI's GPT-4 and automatically posts them to WordPress. It also inserts affiliate links for monetization, fetches relevant images, and formats content for better engagement.

## 📌 Features
- **AI-generated blog posts** using OpenAI's GPT-4.
- **SEO optimization** for better ranking.
- **Automated affiliate link insertion** to monetize content.
- **Automatic image fetching** from free sources.
- **WordPress integration** for instant publishing.
- **Random posting delays** to prevent spam detection.

---

## 🔧 Installation & Setup

### **1️⃣ Prerequisites**
- Python 3.8+
- WordPress website with REST API enabled
- OpenAI API key

### **2️⃣ Clone or Download the Repository**
```
git clone https://your-repository-url.git
cd BlogRepurposingAgent
```

### **3️⃣ Install Dependencies**
```
pip install -r requirements.txt
```

### **4️⃣ Configure `config.json`**
Edit the `config.json` file and enter your credentials:
```json
{
    "openai_api_key": "your-openai-api-key",
    "wordpress_url": "https://yourwebsite.com",
    "wordpress_user": "your-username",
    "wordpress_password": "your-password",
    "affiliate_links": {
        "AI Automation": "https://your-affiliate-link.com",
        "SEO Blogging": "https://your-affiliate-link.com"
    },
    "default_category": "Technology",
    "default_tags": ["AI", "Automation", "Blogging"]
}
```

### **5️⃣ Run the AI Auto-Blogger**
```
python app.py
```

---

## 🛠 Troubleshooting
### 🔹 API Errors
- Ensure your OpenAI API key is valid.
- Check if your WordPress REST API is enabled (`/wp-json/wp/v2/posts`).

### 🔹 Posts Not Publishing
- Verify WordPress credentials in `config.json`.
- Check for missing fields like category or tags.

---

## 📈 Monetization Tips
- Add affiliate links for related products in `config.json`.
- Use `default_tags` to target SEO-specific keywords.
- Create a niche-specific blog for maximum conversions.

---

## 🤝 Support
For support, contact **your-email@example.com**

Happy Blogging! 🚀
