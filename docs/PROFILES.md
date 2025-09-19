# AXP Conformance Profiles

## Overview

AXP defines multiple conformance profiles to address different market segments and regulatory requirements. Each profile builds upon the Core Profile with additional requirements.

## Profile Hierarchy

```
Core Profile (MUST for all)
├── Retail Profile (B2C physical/digital goods)
├── B2B Profile (Business transactions)  
├── Regulated Profile (Compliance-heavy products)
├── Digital Profile (Software/subscriptions)
└── Marketplace Profile (Multi-vendor platforms)
```

## Core Profile (Mandatory)

**All AXP implementations MUST support the Core Profile**

### Required Fields - Product

```json
{
  "spec": "axp",
  "version": "0.1.0",
  "generated_at": "2025-09-18T10:00:00Z",
  "last_verified": "2025-09-18T09:00:00Z",
  "ttl_seconds": 86400,
  "product": {
    "id": "sku_123",
    "title": "Product Name",
    "identifiers": {
      "gtin": "4006381333931",  // At least one identifier
      "mpn": "ABC-123"
    },
    "price": {
      "currency": "EUR",
      "value": 99.99
    },
    "availability": {
      "state": "in_stock"
    },
    "lang": "en",
    "country_of_origin": "DE",
    "provenance": {
      "brand_id": "brand_001",
      "last_verified": "2025-09-18T09:00:00Z",
      "signature": "EdDSA:base64url..."
    }
  }
}
```

### Required Fields - Brand

```json
{
  "brand": {
    "id": "brand_001",
    "legal_name": "Demo Commerce GmbH",
    "domains": ["demo.shop"],
    "founded_year": 2011,
    "headquarters_country": "DE",
    "keys": {
      "jwks_url": "https://demo.shop/.well-known/axp/jwks.json",
      "brand_profile_url": "https://demo.shop/.well-known/axp/brand.json",
      "did": "did:web:demo.shop"
    },
    "last_verified": "2025-09-18T09:00:00Z",
    "ttl_seconds": 604800
  }
}
```

## Retail Profile

**For B2C merchants selling physical or digital goods**

### Additional Requirements

#### Product Extensions
```json
{
  "product": {
    // Core fields plus:
    "taxonomy": {
      "google_product_category": "187",
      "hs_code": "640351",
      "product_type": "Footwear > Sneakers > High-tops"
    },
    "pricing": {
      "list_price": { "currency": "EUR", "value": 129.90 },
      "sale_price": { "currency": "EUR", "value": 99.99 },
      "tax_included": true,
      "valid_from": "2025-09-01T00:00:00Z",
      "valid_to": "2025-09-30T23:59:59Z",
      "unit_price": {
        "value": 3.33,
        "unit": "EUR_per_100g"
      }
    },
    "shipping": {
      "net_weight_grams": 420,
      "ship_weight_grams": 550,
      "package_dimensions_cm": {
        "length": 32,
        "width": 18,
        "height": 12
      },
      "lead_time_days": {
        "p50": 2,
        "p95": 5
      }
    },
    "warranty": {
      "days": 365,
      "type": "manufacturer",
      "service_level": "replace"
    },
    "trust_signals": {
      "review_summary": {
        "avg_rating": 4.5,
        "count_total": 1342,
        "verified_purchase_rate": 0.82
      },
      "return_rate": 0.14,
      "return_reasons": [
        { "reason": "size_issue", "share": 0.56 },
        { "reason": "quality_expectation", "share": 0.22 }
      ]
    },
    "intent_signals": [
      {
        "intent": "daily_commute",
        "share": 0.34,
        "confidence": 0.92,
        "method": "events_plus_text",
        "window_days": 90,
        "sample_size": 812
      }
    ]
  }
}
```

#### Brand Extensions
```json
{
  "brand": {
    // Core fields plus:
    "payments": {
      "methods": ["paypal", "credit_card", "klarna", "afterpay"],
      "chargeback_rate": 0.004,
      "dispute_rate": 0.009
    },
    "fulfillment": {
      "carriers": ["DHL", "DPD", "UPS"],
      "handling_time_days_p50": 1,
      "handling_time_days_p95": 3,
      "on_time_delivery_rate": 0.97,
      "ships_to": ["DE", "AT", "NL", "FR", "IT"]
    },
    "policies": {
      "returns": {
        "days": 30,
        "restocking_fee": 0.0,
        "return_shipping_paid_by": "seller"
      },
      "repairs": {
        "offered": true,
        "warranty_repairs": true,
        "policy_url": "https://demo.shop/repairs"
      }
    },
    "independent_ratings": [
      {
        "source": "Trustpilot",
        "score": 4.6,
        "reviews": 12873,
        "url": "https://trustpilot.com/review/demo.shop",
        "retrieved_at": "2025-09-18T10:00:00Z"
      }
    ]
  }
}
```

## B2B Profile

**For business-to-business transactions**

### Additional Requirements

#### Product Extensions
```json
{
  "product": {
    // Retail fields plus:
    "b2b": {
      "moq": 10,
      "price_tiers": [
        { "min_qty": 10, "price": 89.90 },
        { "min_qty": 50, "price": 79.90, "discount_percent": 10.8 },
        { "min_qty": 100, "price": 69.90, "discount_percent": 21.5 }
      ],
      "lead_time_bulk": {
        "days": 14,
        "for_quantity": 500
      },
      "payment_terms": "2/10 Net 30",
      "incoterms": "DDP"
    },
    "compatibility": {
      "works_with": ["sku_456", "sku_789"],
      "spare_parts": ["sku_lace_red", "sku_insole_comfort"],
      "bundles": [
        {
          "bundle_id": "bundle_starter",
          "products": ["sku_123", "sku_456"],
          "discount": 15
        }
      ]
    }
  }
}
```

#### Brand Extensions
```json
{
  "brand": {
    // Retail fields plus:
    "legal": {
      "registration_number": "HRB 12345",
      "vat_id": "DE123456789",
      "eori": "DE1234567890123",
      "duns": "123456789",
      "gln": "4001234567890",
      "legal_form": "GmbH",
      "beneficial_owners": [
        { "name": "Max Mustermann", "ownership_percent": 66.7 }
      ]
    },
    "payments": {
      "payment_terms": {
        "b2b_net_days": 30,
        "early_payment_discount": 0.02
      }
    },
    "compliance": {
      "liability_insurance": {
        "coverage_eur": 5000000,
        "insurer": "Allianz",
        "valid_until": "2026-12-31"
      }
    }
  }
}
```

## Regulated Profile

**For products with compliance requirements**

### Additional Requirements

#### Product Extensions
```json
{
  "product": {
    // B2B fields plus:
    "regulatory": {
      "hazmat": false,
      "battery": {
        "present": true,
        "type": "lithium_ion",
        "watt_hours": 36.5
      },
      "age_rating": "18plus",
      "ce_marking": true,
      "fda_approved": false,
      "eco_labels": [
        "EU_energy_label_A",
        "Energy_Star"
      ]
    }
  }
}
```

#### Brand Extensions
```json
{
  "brand": {
    // B2B fields plus:
    "compliance": {
      "weee_categories": ["small_it", "telecom"],
      "epr_packaging": true,
      "rohs": true,
      "reach": true,
      "certifications": [
        {
          "type": "ISO9001",
          "issuer": "TÜV SÜD",
          "valid_until": "2026-06-30",
          "certificate_url": "https://cert.tuv.com/..."
        },
        {
          "type": "ISO14001",
          "issuer": "Bureau Veritas",
          "valid_until": "2027-01-15",
          "certificate_url": "https://cert.bureauveritas.com/..."
        }
      ]
    },
    "policies": {
      "sustainability": {
        "carbon_neutral_shipping": true,
        "recycled_packaging": true,
        "take_back_program": true,
        "sustainability_report_url": "https://demo.shop/sustainability"
      }
    }
  }
}
```

## Digital Profile

**For software, subscriptions, and digital content**

### Additional Requirements

#### Product Extensions
```json
{
  "product": {
    // Core fields plus:
    "digital": {
      "license_type": "subscription",
      "delivery_method": "api",
      "platform_requirements": [
        "Windows 10 version 1909+",
        "macOS 12.0+",
        "Ubuntu 20.04+"
      ],
      "file_size_mb": 125.5,
      "drm": false,
      "subscription": {
        "billing_period": "monthly",
        "auto_renewal": true,
        "cancellation_period_days": 30
      }
    },
    "pricing": {
      "subscription_tiers": [
        {
          "name": "Basic",
          "monthly_price": 9.99,
          "annual_price": 99.99,
          "features": ["Feature A", "Feature B"]
        },
        {
          "name": "Professional",
          "monthly_price": 29.99,
          "annual_price": 299.99,
          "features": ["All Basic", "Feature C", "Feature D"]
        }
      ]
    }
  }
}
```

## Marketplace Profile

**For multi-vendor platforms**

### Additional Requirements

#### Platform Extensions
```json
{
  "marketplace": {
    "platform_id": "marketplace_001",
    "vendor": {
      "id": "vendor_123",
      "name": "Vendor Name",
      "rating": 4.7,
      "member_since": "2019-03-15"
    },
    "fulfillment": {
      "type": "merchant",  // or "platform"
      "sla": {
        "processing_days": 2,
        "shipping_days": 3
      }
    },
    "commission": {
      "rate": 0.15,
      "category_specific": {
        "electronics": 0.08,
        "fashion": 0.20
      }
    },
    "verification": {
      "vendor_verified": true,
      "product_authenticated": false,
      "platform_guarantee": true
    }
  }
}
```

## Profile Validation

### Tools for Profile Compliance

```bash
# Validate against specific profile
axp validate --profile retail product.json

# Check profile completeness
axp profile-check --profile b2b bundle.zip

# Generate profile report
axp conformance --detailed --profile regulated
```

### Profile Transition Path

```
1. Start with Core Profile (minimum viable)
2. Add Retail Profile (consumer features)
3. Extend to B2B if needed (bulk ordering)
4. Add Regulated for compliance (certifications)
5. Include Digital for software (licensing)
6. Implement Marketplace for platforms
```

## Profile Selection Guide

| Use Case | Recommended Profile |
|----------|-------------------|
| Small online shop | Core + Retail |
| Enterprise supplier | Core + B2B + Regulated |
| Software vendor | Core + Digital |
| Electronics retailer | Core + Retail + Regulated |
| Fashion marketplace | Core + Retail + Marketplace |
| Industrial equipment | Core + B2B + Regulated |
| Digital downloads | Core + Digital |
| Pharmaceutical | Core + Retail + Regulated |

---

*Profiles are cumulative - each builds on previous requirements. Start with Core and add profiles as needed.*
