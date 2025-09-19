# AXP Brand Profile Schema

## Overview

The Brand Profile schema represents the complete identity of a merchant or brand, including trust signals, operational metrics, and verifiable credentials. This schema enables AI agents to understand not just what a brand sells, but who they are, their values, and their trustworthiness.

## Schema Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://agentic-commerce.org/axp/v0.1/schemas/brand_profile",
  "title": "AXP Brand Profile",
  "type": "object"
}
```

## Core Fields

### Protocol Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `spec` | `string` | ✅ | Must be `"axp"` |
| `version` | `string` | ✅ | SemVer format (e.g., `"0.1.0"`) |
| `generated_at` | `string` | ✅ | ISO 8601 timestamp |

### Brand Object

The main `brand` object contains all brand-specific information:

#### Identity Fields

| Field | Type | Required | Description | How to Measure |
|-------|------|----------|-------------|----------------|
| `id` | `string` | ✅ | Unique brand identifier | Internal system ID or UUID |
| `legal_name` | `string` | ✅ | Registered company name | From business registration |
| `domains` | `array[string]` | ✅ | Associated domains | DNS records, SSL certificates |
| `founded_year` | `integer` | ❌ | Year established (1800-2100) | Business registration |
| `employee_count` | `integer` | ❌ | Number of employees | HR systems, public filings |
| `customer_count_estimate` | `integer` | ❌ | Active customers | CRM, order management |
| `headquarters_country` | `string` | ❌ | ISO 3166-1 alpha-2 code | Business registration |

#### Trust Signals

##### Certifications

**What**: Industry certifications and compliance badges  
**Format**: Array of strings  
**Examples**: `["ISO9001", "ClimatePartner", "B-Corp", "Fair Trade"]`  
**How to Measure**:
- Document certification IDs and expiry dates
- Store certification documents/PDFs
- Implement renewal tracking
- Verify with issuing bodies

##### Independent Ratings

**Structure**:
```json
{
  "source": "Trustpilot",
  "score": 4.6,
  "reviews": 12873,
  "url": "https://trustpilot.com/review/example.com"
}
```

**How to Collect**:
1. **API Integration**: Connect to rating platform APIs
2. **Web Scraping**: For platforms without APIs (with permission)
3. **Manual Updates**: Monthly verification of scores
4. **Historical Tracking**: Store score changes over time

**Supported Sources**:
- Trustpilot
- Google Reviews
- Better Business Bureau (BBB)
- Industry-specific (e.g., Shopauskunft.de for German markets)

#### Operational Metrics

##### Customer Satisfaction (CSAT)

**Field**: `csat`  
**Type**: `number` (0.0-1.0)  
**Description**: Customer satisfaction score  

**How to Measure**:
```python
# Post-purchase survey
satisfaction_responses = [5, 4, 5, 3, 5, 4, 5]  # 1-5 scale
csat = sum(r >= 4 for r in satisfaction_responses) / len(satisfaction_responses)
# Result: 0.86 (86% satisfied)
```

**Collection Methods**:
- Email surveys 24-48 hours post-delivery
- In-app feedback widgets
- SMS surveys for mobile-first customers
- Quarterly relationship surveys

##### Net Promoter Score (NPS)

**Field**: `nps`  
**Type**: `integer` (-100 to 100)  
**Description**: Likelihood to recommend  

**How to Calculate**:
```python
# Survey: "How likely are you to recommend us?" (0-10)
responses = [9, 10, 8, 6, 9, 10, 7, 8, 9, 10]

promoters = sum(1 for r in responses if r >= 9)  # 9-10
detractors = sum(1 for r in responses if r <= 6)  # 0-6
nps = ((promoters - detractors) / len(responses)) * 100
# Result: NPS = 50
```

**Best Practices**:
- Ask quarterly for B2C, bi-annually for B2B
- Segment by customer lifetime value
- Track trend over time (more important than absolute value)
- Follow up with open-ended "why" questions

##### Return Rate

**Field**: `return_rate`  
**Type**: `number` (0.0-1.0)  
**Description**: Percentage of orders returned  

**How to Calculate**:
```sql
-- Monthly calculation
SELECT 
  COUNT(DISTINCT return_id) / COUNT(DISTINCT order_id) AS return_rate
FROM orders
WHERE order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
```

**Benchmarks by Industry**:
- Apparel: 20-30% (normal)
- Electronics: 8-12% (normal)
- Furniture: 5-10% (normal)
- Beauty: 5-10% (normal)

##### Service Level Agreement (SLA)

**Structure**:
```json
"service_sla": {
  "first_response_hours": 4,
  "resolution_hours_p50": 24
}
```

**How to Measure**:
```python
# From support ticket system
tickets = get_support_tickets(last_90_days)

first_response_times = [
    (ticket.first_response - ticket.created).hours 
    for ticket in tickets
]
resolution_times = [
    (ticket.resolved - ticket.created).hours 
    for ticket in tickets if ticket.resolved
]

sla = {
    "first_response_hours": statistics.median(first_response_times),
    "resolution_hours_p50": statistics.median(resolution_times)
}
```

#### Unique Value Propositions

**Field**: `unique_value_props`  
**Type**: `array[string]`  

**Examples**:
- "Lifetime repair service"
- "Local production within 50km"
- "Open spare parts catalog"
- "Carbon neutral shipping"
- "24/7 expert support"

**How to Identify**:
1. **Competitive Analysis**: What do you offer that others don't?
2. **Customer Feedback**: Why do customers choose you?
3. **Internal Capabilities**: Unique processes or expertise
4. **Verification**: Can you prove/measure each claim?

#### Trust Factors

**Structure**:
```json
"trust_factors": {
  "badges": ["PCI DSS ready", "GDPR controls"],
  "warranties": [
    {
      "name": "Extended warranty",
      "duration_days": 730
    }
  ],
  "data_provenance": "signed_by_brand_key"
}
```

## Data Collection Guidelines

### 1. Initial Setup

```python
# Brand profile generator example
from datetime import datetime
import json

def generate_brand_profile(company_data):
    profile = {
        "spec": "axp",
        "version": "0.1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "brand": {
            "id": company_data["id"],
            "legal_name": company_data["name"],
            "domains": extract_domains(company_data),
            "certifications": fetch_certifications(company_data),
            "independent_ratings": collect_ratings(company_data),
            "csat": calculate_csat(company_data["survey_data"]),
            "nps": calculate_nps(company_data["nps_responses"]),
            "return_rate": calculate_return_rate(company_data["orders"]),
            # ... additional fields
        }
    }
    return profile
```

### 2. Data Sources Integration

| Metric | Primary Source | Secondary Source | Update Frequency |
|--------|---------------|------------------|------------------|
| CSAT | Survey platform | CRM system | Weekly |
| NPS | Email surveys | In-app feedback | Quarterly |
| Return Rate | Order Management | ERP | Daily |
| Reviews | Platform APIs | Manual checks | Daily |
| Certifications | Document store | Public registries | Quarterly |
| Employee Count | HR system | LinkedIn | Monthly |

### 3. Quality Assurance

```python
# Validation checklist
def validate_brand_profile(profile):
    checks = {
        "has_required_fields": all(
            field in profile["brand"] 
            for field in ["id", "legal_name", "domains"]
        ),
        "valid_csat": 0 <= profile["brand"].get("csat", 0) <= 1,
        "valid_nps": -100 <= profile["brand"].get("nps", 0) <= 100,
        "valid_return_rate": 0 <= profile["brand"].get("return_rate", 0) <= 1,
        "domains_reachable": verify_domains(profile["brand"]["domains"]),
        "certifications_valid": verify_certifications(
            profile["brand"].get("certifications", [])
        )
    }
    return all(checks.values()), checks
```

## Implementation Examples

### 1. Shopware Integration

```php
// Shopware 6 Brand Profile Generator
class BrandProfileGenerator
{
    public function generate(Context $context): array
    {
        $shopConfig = $this->systemConfigService->get('core.basicInformation');
        $reviews = $this->getAggregatedReviews($context);
        $orders = $this->orderRepository->search(new Criteria(), $context);
        
        return [
            'spec' => 'axp',
            'version' => '0.1.0',
            'generated_at' => (new \DateTime())->format('c'),
            'brand' => [
                'id' => $shopConfig['shopId'],
                'legal_name' => $shopConfig['companyName'],
                'domains' => [$shopConfig['domain']],
                'csat' => $this->calculateCSAT($reviews),
                'return_rate' => $this->calculateReturnRate($orders),
                // ... additional metrics
            ]
        ];
    }
}
```

### 2. WooCommerce Integration

```php
// WooCommerce Brand Profile Plugin
add_action('rest_api_init', function () {
    register_rest_route('axp/v1', '/brand-profile', [
        'methods' => 'GET',
        'callback' => function() {
            $profile = [
                'spec' => 'axp',
                'version' => '0.1.0',
                'generated_at' => date('c'),
                'brand' => [
                    'id' => get_option('woocommerce_store_id'),
                    'legal_name' => get_bloginfo('name'),
                    'domains' => [parse_url(home_url(), PHP_URL_HOST)],
                    'return_rate' => calculate_wc_return_rate(),
                    // ... additional fields
                ]
            ];
            return new WP_REST_Response($profile, 200);
        }
    ]);
});
```

## Best Practices

### 1. Data Freshness

- **Real-time metrics**: Inventory, availability
- **Daily updates**: Reviews, ratings, return rates
- **Weekly updates**: CSAT scores
- **Monthly updates**: Employee count, certifications
- **Quarterly updates**: NPS scores

### 2. Privacy Compliance

- Never include PII in brand profiles
- Aggregate metrics only (no individual customer data)
- Comply with GDPR, CCPA requirements
- Implement data retention policies

### 3. Verification & Trust

- Sign all brand profiles cryptographically
- Provide evidence links for claims
- Update expired certifications promptly
- Monitor for review manipulation

## Scoring Recommendations

Agents should weight brand signals based on use case:

| Use Case | Primary Signals | Secondary Signals |
|----------|----------------|-------------------|
| Luxury Goods | Certifications, NPS | Return Rate, Reviews |
| Daily Essentials | Reviews, CSAT | Response Time, Availability |
| B2B Procurement | SLA, Certifications | Employee Count, Founded Year |
| Sustainable Shopping | Certifications, Values | Local Production, Return Rate |

## Integration with AP2 Protocol

When integrating with AP2 payment mandates:

```json
{
  "ap2.mandates.CartMandate": {
    // ... cart details
    "merchant_evidence": {
      "brand_profile_signature": "...",
      "trust_score": 0.89,
      "verification_url": "https://example.com/.well-known/axp/brand"
    }
  }
}
```

This allows payment processors and dispute resolution to consider brand trust signals.

## References

- [ISO 9001 Quality Management](https://www.iso.org/iso-9001-quality-management.html)
- [Net Promoter System](https://www.netpromotersystem.com/about/)
- [CSAT Measurement Guide](https://www.qualtrics.com/experience-management/customer/what-is-csat/)
- [PCI DSS Compliance](https://www.pcisecuritystandards.org/)
