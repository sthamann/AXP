# AXP Product Schema

## Overview

The Product schema represents comprehensive product data including soft signals, trust factors, experiences, and intent mapping. This enables AI agents to understand not just what a product is, but why customers buy it, what makes it unique, and how it fits different use cases.

## Core Structure

```json
{
  "product": {
    "id": "sku_123",
    "title": "Premium Running Shoes",
    "price": {"currency": "EUR", "value": 129.90},
    "availability": {"state": "in_stock", "quantity": 220},
    // ... additional fields
  }
}
```

## Field Documentation

### Basic Product Information

| Field | Type | Required | Description | How to Populate |
|-------|------|----------|-------------|-----------------|
| `id` | `string` | ✅ | Unique SKU | Product management system |
| `parent_id` | `string/null` | ❌ | Parent for variants | PIM system |
| `title` | `string` | ✅ | Product name | Product catalog |
| `short_desc` | `string` | ❌ | Brief description (max 200 chars) | Marketing copy |
| `price` | `object` | ✅ | Pricing information | Pricing engine |
| `availability` | `object` | ✅ | Stock status | Inventory system |

### Technical Specifications

**Field**: `tech_specs`  
**Type**: `object` (flexible schema)

**Common Properties**:
```json
"tech_specs": {
  "material": "Premium leather upper, rubber sole",
  "weight_grams": 420,
  "sizes": ["38", "39", "40", "41", "42", "43", "44", "45"],
  "care": "Hand wash cold, air dry",
  "dimensions_cm": {"length": 30, "width": 12, "height": 10},
  "color": "Red/White",
  "model_year": 2025
}
```

**Industry-Specific Examples**:

<details>
<summary>Electronics</summary>

```json
"tech_specs": {
  "processor": "Apple M3",
  "ram_gb": 16,
  "storage_gb": 512,
  "battery_wh": 52.6,
  "display": "13.6-inch Retina",
  "ports": ["2x USB-C", "1x MagSafe", "1x 3.5mm"],
  "wireless": ["Wi-Fi 6E", "Bluetooth 5.3"]
}
```
</details>

<details>
<summary>Fashion</summary>

```json
"tech_specs": {
  "material": "100% Organic Cotton",
  "fit": "Regular",
  "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
  "care": "Machine wash 30°C",
  "origin": "Made in Portugal",
  "fabric_weight_gsm": 180
}
```
</details>

### Media & Content

**Structure**:
```json
"media": {
  "images": [...],
  "documents": [...],
  "videos": [...]
}
```

#### Images with AI Captions

**Purpose**: Enable semantic search and accessibility

```json
"images": [
  {
    "url": "https://cdn.shop.com/products/shoe-red-1.jpg",
    "machine_captions": [
      {"lang": "en", "text": "Red running shoe on white background"},
      {"lang": "de", "text": "Roter Laufschuh auf weißem Hintergrund"}
    ],
    "embeddings": {
      "clip": {
        "dim": 768,
        "vector": "base64-encoded-float32-array"
      }
    }
  }
]
```

**How to Generate Captions**:
```python
# Using Google Cloud Vision API
from google.cloud import vision
import base64

def generate_image_captions(image_url):
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_url
    
    # Get labels
    response = client.label_detection(image=image)
    labels = [label.description for label in response.label_annotations]
    
    # Get localized objects
    objects = client.object_localization(image=image)
    
    # Generate caption
    caption = generate_caption_from_labels(labels, objects)
    
    return caption
```

**How to Generate Embeddings**:
```python
# Using CLIP for image embeddings
from transformers import CLIPModel, CLIPProcessor
import torch
import base64
import numpy as np

def generate_clip_embedding(image_url):
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    image = Image.open(requests.get(image_url, stream=True).raw)
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    
    # Convert to base64
    embedding_np = embedding.numpy().flatten()
    embedding_b64 = base64.b64encode(embedding_np.astype(np.float32).tobytes()).decode()
    
    return {
        "dim": len(embedding_np),
        "vector": embedding_b64
    }
```

### Soft Signals (Differentiators)

These scores help agents understand what makes a product special:

| Signal | Range | Description | How to Calculate |
|--------|-------|-------------|------------------|
| `uniqueness_score` | 0-1 | How distinctive/rare | See calculation below |
| `craftsmanship_score` | 0-1 | Quality of construction | Reviews + materials + price tier |
| `sustainability_score` | 0-1 | Environmental impact | Certifications + materials + process |
| `innovation_score` | 0-1 | Technical advancement | Features + patents + awards |

#### Uniqueness Score Calculation

```python
def calculate_uniqueness_score(product, market_data):
    """
    Factors:
    - Rarity of features (0-0.3)
    - Price positioning (0-0.2)
    - Brand exclusivity (0-0.2)
    - Limited availability (0-0.15)
    - Design awards (0-0.15)
    """
    
    score = 0.0
    
    # Feature rarity
    unique_features = identify_unique_features(product, market_data)
    score += min(0.3, len(unique_features) * 0.1)
    
    # Price positioning (premium adds uniqueness)
    price_percentile = calculate_price_percentile(product.price, market_data)
    if price_percentile > 0.8:  # Top 20% price
        score += 0.2
    elif price_percentile > 0.6:  # Top 40%
        score += 0.1
    
    # Brand exclusivity
    if product.brand in LUXURY_BRANDS:
        score += 0.2
    elif product.brand in PREMIUM_BRANDS:
        score += 0.1
    
    # Limited availability
    if product.availability.quantity < 100:
        score += 0.15
    elif product.availability.state == "preorder":
        score += 0.1
    
    # Design awards
    awards = count_design_awards(product)
    score += min(0.15, awards * 0.05)
    
    return round(score, 2)
```

#### Craftsmanship Score Calculation

```python
def calculate_craftsmanship_score(product, reviews):
    """
    Factors:
    - Material quality (0-0.3)
    - Manufacturing origin (0-0.2)
    - Durability mentions in reviews (0-0.25)
    - Warranty length (0-0.25)
    """
    
    score = 0.0
    
    # Material quality
    materials = extract_materials(product.tech_specs)
    material_scores = {
        "genuine_leather": 0.3,
        "organic_cotton": 0.25,
        "recycled_materials": 0.2,
        "synthetic": 0.1
    }
    score += max([material_scores.get(m, 0.05) for m in materials])
    
    # Manufacturing origin
    origin_scores = {
        "handmade": 0.2,
        "made_in_italy": 0.15,
        "made_in_japan": 0.15,
        "made_in_germany": 0.15,
        "local_production": 0.1
    }
    score += origin_scores.get(product.origin, 0.05)
    
    # Review analysis
    quality_mentions = analyze_reviews_for_quality(reviews)
    score += min(0.25, quality_mentions * 0.05)
    
    # Warranty
    warranty_years = product.warranty_days / 365
    if warranty_years >= 2:
        score += 0.25
    elif warranty_years >= 1:
        score += 0.15
    else:
        score += 0.05
    
    return round(score, 2)
```

### Trust Signals

#### Review Summary

```json
"review_summary": {
  "avg_rating": 4.5,
  "count_total": 1342,
  "count_verified": 1180,
  "distribution": {
    "5": 720,
    "4": 380,
    "3": 140,
    "2": 72,
    "1": 30
  },
  "top_positive": ["Comfortable", "Great design", "Durable"],
  "top_negative": ["Runs small", "Expensive"]
}
```

**How to Extract Topics**:
```python
from collections import Counter
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_review_topics(reviews, sentiment="positive"):
    topics = []
    
    for review in reviews:
        if (sentiment == "positive" and review.rating >= 4) or \
           (sentiment == "negative" and review.rating <= 2):
            doc = nlp(review.text)
            
            # Extract adjectives and noun phrases
            for token in doc:
                if token.pos_ == "ADJ":
                    topics.append(token.text.lower())
            
            for chunk in doc.noun_chunks:
                if any(token.pos_ == "ADJ" for token in chunk):
                    topics.append(chunk.text.lower())
    
    # Return top topics
    topic_counts = Counter(topics)
    return [topic for topic, _ in topic_counts.most_common(5)]
```

#### Return Analysis

```json
"return_reasons": [
  {"reason": "size_issue", "share": 0.56},
  {"reason": "color_mismatch", "share": 0.18},
  {"reason": "quality_expectation", "share": 0.12},
  {"reason": "changed_mind", "share": 0.08},
  {"reason": "damaged", "share": 0.06}
]
```

**SQL Query for Return Reasons**:
```sql
WITH return_analysis AS (
  SELECT 
    product_id,
    return_reason,
    COUNT(*) as reason_count,
    SUM(COUNT(*)) OVER (PARTITION BY product_id) as total_returns
  FROM returns
  WHERE return_date >= DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY)
  GROUP BY product_id, return_reason
)
SELECT 
  product_id,
  return_reason as reason,
  ROUND(reason_count::DECIMAL / total_returns, 2) as share
FROM return_analysis
WHERE product_id = 'sku_123'
ORDER BY share DESC;
```

### Intent Signals

Understanding why customers buy:

```json
"intent_signals": [
  {"intent": "daily_commute", "share": 0.34},
  {"intent": "sports_activity", "share": 0.28},
  {"intent": "fashion_statement", "share": 0.38}
]
```

**How to Derive Intent**:

1. **Order Context Analysis**:
```python
def analyze_purchase_intent(order_data):
    """Analyze cart composition and timing"""
    intents = []
    
    # Check cart composition
    if has_complementary_sports_items(order_data.cart):
        intents.append("sports_activity")
    
    # Check purchase timing
    if is_before_school_season(order_data.date):
        intents.append("back_to_school")
    
    # Check customer segment
    if order_data.customer.age_group == "teen":
        intents.append("fashion_statement")
    
    return intents
```

2. **Review Mining**:
```python
intent_keywords = {
    "daily_commute": ["everyday", "work", "commute", "daily"],
    "sports_activity": ["running", "gym", "workout", "training"],
    "fashion_statement": ["style", "look", "trendy", "outfit"],
    "gift": ["present", "gift", "birthday", "christmas"]
}

def extract_intent_from_reviews(reviews):
    intent_counts = Counter()
    
    for review in reviews:
        text_lower = review.text.lower()
        for intent, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                intent_counts[intent] += 1
    
    total = sum(intent_counts.values())
    return [
        {"intent": intent, "share": round(count/total, 2)}
        for intent, count in intent_counts.most_common()
    ]
```

### Experience Capsules

Interactive product experiences:

```json
"experiences": {
  "capsules": [
    {
      "id": "cap_sneaker_3d",
      "title": "3D configurator",
      "capsule_uri": "axp://capsules/cap_sneaker_3d.zip",
      "modality": "canvas3d",
      "preferred_size": {"width": 720, "height": 480},
      "params_schema": {
        "type": "object",
        "properties": {
          "color": {"enum": ["red", "black", "white"]},
          "size": {"type": "string"}
        }
      }
    }
  ]
}
```

**Modality Types**:
- `canvas3d`: 3D model viewer
- `ar_preview`: Augmented reality
- `configurator`: Product customization
- `size_guide`: Interactive sizing
- `comparison`: Feature comparison tool
- `virtual_try_on`: Camera-based try-on

## Implementation Patterns

### 1. Shopware 6 Product Enrichment

```php
class ProductEnricher
{
    public function enrich(ProductEntity $product): array
    {
        $reviews = $this->reviewRepository->search(
            new Criteria([$product->getId()]),
            $context
        );
        
        return [
            'product' => [
                'id' => $product->getProductNumber(),
                'title' => $product->getTranslation('name'),
                'price' => [
                    'currency' => 'EUR',
                    'value' => $product->getPrice()->first()->getGross()
                ],
                'soft_signals' => [
                    'uniqueness_score' => $this->calculateUniqueness($product),
                    'craftsmanship_score' => $this->calculateCraftsmanship($product),
                    'sustainability_score' => $this->calculateSustainability($product),
                    'innovation_score' => $this->calculateInnovation($product)
                ],
                'trust_signals' => [
                    'review_summary' => $this->summarizeReviews($reviews),
                    'return_rate' => $this->calculateReturnRate($product)
                ],
                'intent_signals' => $this->analyzeIntent($product)
            ]
        ];
    }
}
```

### 2. Real-time Signal Updates

```python
# Using Apache Kafka for real-time updates
from kafka import KafkaProducer
import json

class SignalUpdater:
    def __init__(self):
        self.producer = KafkaProducer(
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def update_review_signals(self, product_id, new_review):
        # Recalculate review summary
        summary = self.recalculate_review_summary(product_id, new_review)
        
        # Send update
        self.producer.send('axp.product.updates', {
            'product_id': product_id,
            'update_type': 'review_summary',
            'data': summary,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def update_inventory(self, product_id, quantity):
        self.producer.send('axp.product.updates', {
            'product_id': product_id,
            'update_type': 'availability',
            'data': {
                'state': 'in_stock' if quantity > 0 else 'out_of_stock',
                'quantity': quantity
            },
            'timestamp': datetime.utcnow().isoformat()
        })
```

## Agent Ranking Hints

Help agents prioritize signals:

```json
"agent_ranking_hint": {
  "primary": ["uniqueness_score", "review_summary.avg_rating"],
  "secondary": ["return_rate", "sustainability_score"],
  "context": {
    "luxury_shopping": ["uniqueness_score", "craftsmanship_score"],
    "value_shopping": ["review_summary.avg_rating", "return_rate"],
    "sustainable_shopping": ["sustainability_score", "certifications"]
  }
}
```

## Best Practices

### 1. Data Quality

- **Validation**: Ensure all scores are normalized (0-1)
- **Evidence**: Provide links/proof for all claims
- **Freshness**: Update inventory hourly, reviews daily
- **Completeness**: Fill as many optional fields as possible

### 2. Performance Optimization

```python
# Cache expensive calculations
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_product_signals(product_id: str, cache_key: str):
    """Cache expensive signal calculations"""
    return {
        'uniqueness_score': calculate_uniqueness(product_id),
        'craftsmanship_score': calculate_craftsmanship(product_id),
        'sustainability_score': calculate_sustainability(product_id)
    }

# Generate cache key from product state
def generate_cache_key(product):
    relevant_data = f"{product.updated_at}{product.review_count}{product.price}"
    return hashlib.md5(relevant_data.encode()).hexdigest()
```

### 3. Progressive Enhancement

Start with basic required fields and progressively add:

**Phase 1**: Basic catalog (id, title, price, availability)  
**Phase 2**: Add reviews and media  
**Phase 3**: Add soft signals  
**Phase 4**: Add intent signals and experiences  
**Phase 5**: Add real-time updates

## Integration with AP2

When creating cart mandates, include product evidence:

```json
{
  "ap2.mandates.CartMandate": {
    "contents": {
      "displayItems": [
        {
          "label": "Premium Running Shoes",
          "amount": {"currency": "EUR", "value": 129.90},
          "metadata": {
            "axp_product_id": "sku_123",
            "uniqueness_score": 0.82,
            "sustainability_score": 0.61,
            "review_rating": 4.5
          }
        }
      ]
    }
  }
}
```

## References

- [Schema.org Product](https://schema.org/Product)
- [Google Merchant Center Specifications](https://support.google.com/merchants/answer/7052112)
- [CLIP Model for Embeddings](https://github.com/openai/CLIP)
- [Review Mining Techniques](https://arxiv.org/abs/2104.07156)
