# 🛒 Walmart Scraper API (FastAPI)

A production-ready **FastAPI-based Walmart Product Scraper API** that extracts structured product details, reviews, nutrition info, specifications, and more directly from Walmart product pages.  

## 🚀 Features
- Input: Walmart **Product ID** or **Product URL**  
- Extracts:
  - Product name, brand, price, UPC, size (oz)  
  - Short + Long descriptions  
  - Nutrition facts & ingredients  
  - Specifications (calories, allergens, etc.)  
  - Location info (state, city, postal code)  
  - Customer reviews (title, text, nickname, rating)  
  - Highlights (pack size, confidently badges)  
- Clean **JSON output**  
- FastAPI **Swagger UI** at `/docs`  

---

## ⚙️ Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/your-username/walmart-scraper-api.git
   cd walmart-scraper-api
Create virtual environment (optional but recommended):

bash
Copy code
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
▶️ Run Locally
bash
Copy code
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Open in browser:

API UI → http://127.0.0.1:8000/docs

Web UI → http://127.0.0.1:8000/

🌐 Deploy on Render
Push your code to a GitHub repo.

Create a new Web Service on Render.

Set Start Command as:

bash
Copy code
uvicorn app:app --host 0.0.0.0 --port $PORT
Add requirements.txt in root of repo.

Deploy 🚀

📝 API Usage
Example cURL
bash
Copy code
curl -X POST "https://your-render-url.onrender.com/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.walmart.com/ip/123456789"}'
Example Response
json
Copy code
{
  "product_id": "123456789",
  "name": "Walmart Sample Product",
  "brand": "Great Value",
  "price": 12.99,
  "upc": "000123456789",
  "short_description": "Delicious and fresh...",
  "long_description": "Full product description...",
  "nutrition": { "calories": 120, "allergens": "Milk, Soy" },
  "reviews": [
    { "nickname": "JohnD", "title": "Great!", "rating": 5, "text": "Loved it!" }
  ]
}
📂 Project Structure
csharp
Copy code
.
├── app.py          
├── requirements.txt   
├── README.md         
└── static/            
