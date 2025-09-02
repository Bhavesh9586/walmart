# Walmart Product API

A Flask-based REST API that extracts detailed product information from Walmart product URLs.

## Features

- Extract product title, price, rating, brand, description
- Get product images
- Check availability status
- Structured data extraction
- Error handling and validation
- CORS enabled for frontend integration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### GET /
Returns API information and usage instructions.

### POST /extract
Extracts product details from a Walmart URL.

**Request Body:**
```json
{
  "url": "https://www.walmart.com/ip/product-name/product-id"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Product Name",
    "price": "$XX.XX",
    "rating": "4.5/5",
    "brand": "Brand Name",
    "description": "Product description...",
    "images": ["image1.jpg", "image2.jpg"],
    "availability": "In Stock",
    "product_id": "123456789",
    "url": "original_url",
    "scraped_at": "2024-01-01 12:00:00"
  }
}
```

### GET /health
Health check endpoint.

## Usage Example

```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.walmart.com/ip/Apple-iPhone-15-128GB-Blue/5051007897"}'
```

## Error Handling

The API handles various error scenarios:
- Invalid URLs
- Network errors
- Scraping failures
- Missing request data

## Notes

- The API uses web scraping, so it may need updates if Walmart changes their website structure
- Rate limiting is recommended for production use
- Some product details may not be available for all products
