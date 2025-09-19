# AXP Protocol Specification v0.1

## Table of Contents

### Part 1: Normative Specification
1. [Introduction](#introduction)
2. [Conformance Requirements](#conformance-requirements)
3. [Namespace and Versioning](#namespace-and-versioning)
4. [Canonical JSON and Signatures](#canonical-json-and-signatures)
5. [Data Model](#data-model)
6. [Export Format](#export-format)
7. [MCP Protocol](#mcp-protocol)
8. [Experience Capsules](#experience-capsules)
9. [Security Model](#security-model)

### Part 2: Implementation Profiles
10. [Controlled Vocabularies](#controlled-vocabularies)
11. [Scoring Guidelines](#scoring-guidelines)
12. [Internationalization](#internationalization)
13. [Real-time Updates](#real-time-updates)

### Part 3: Integration
14. [AP2 Evidence Chain](#ap2-evidence-chain)
15. [Compliance Suite](#compliance-suite)

## Introduction

The Agentic Experience Protocol (AXP) defines a standardized format for exposing rich commerce experiences to AI agents. It focuses on trust, uniqueness, and interactive experiences that go beyond traditional product catalogs.

### Design Principles

1. **Agent-First**: Optimized for machine consumption and decision-making
2. **Trust by Design**: Cryptographic provenance and verification built-in
3. **Experience-Rich**: Interactive capsules for immersive product exploration
4. **Privacy-Preserving**: No PII, strict sandboxing, minimal data exposure
5. **Interoperable**: Works seamlessly with AP2 for payments

## Conformance Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

### Conformance Levels

1. **Core Profile**: Minimum requirements for AXP compliance
2. **Retail Profile**: Additional requirements for retail commerce
3. **B2B Profile**: Extended requirements for B2B transactions

### Core Requirements

- **MUST**: Every AXP document MUST carry `spec`, `version`, and `generated_at` fields
- **MUST**: Every signed AXP object MUST follow the AXP Canonical JSON rules
- **SHOULD**: Providers SHOULD implement the Retail Core Profile
- **MAY**: Providers MAY extend with industry-specific profiles

## Namespace and Versioning

- **Namespace**: `axp.v0_1`
- **Extension URI**: `https://agentic-commerce.org/axp/v0.1`
- **Version Format**: Semantic Versioning (SemVer)
- **Required Fields**: All top-level objects MUST include:
  - `spec`: "axp" (MUST)
  - `version`: "0.1.0" (MUST)
  - `generated_at`: ISO 8601 timestamp with Z suffix (MUST)
  - `last_verified`: ISO 8601 timestamp (SHOULD)

## Canonical JSON and Signatures

### Canonical JSON Rules

**MUST**: Before signing, apply these transformations:
1. Remove `signature` field if present
2. Sort object keys lexicographically
3. Format numbers as IEEE 754 double precision without leading zeros
4. Format timestamps in ISO 8601 with Z suffix (UTC only)
5. Normalize Unicode strings to NFC form
6. No whitespace outside of string values

### Signature Requirements

**MUST**: Support Ed25519 and RS256 algorithms
**MUST**: Keys distributed via `did:web` or JWKS endpoint
**SHOULD**: Rotate keys quarterly, old keys retained for verification only
**MAY**: Use on-chain anchoring as additional proof

### Signature Format

```json
{
  "data": { /* canonicalized content */ },
  "signature": {
    "alg": "EdDSA",
    "kid": "did:web:demo.shop#axp-2025",
    "sig": "base64url...",
    "ts": "2025-09-18T10:00:00Z"
  }
}

## Data Model

### Brand Profile

Represents the merchant/brand identity with trust signals and operational metrics.

```json
{
  "spec": "axp",
  "version": "0.1.0",
  "generated_at": "2025-09-18T10:00:00Z",
  "brand": {
    "id": "brand_001",
    "legal_name": "Demo Commerce GmbH",
    "founded_year": 2011,
    "employee_count": 480,
    "customer_count_estimate": 55000,
    "headquarters_country": "DE",
    "domains": ["demo.shop"],
    "certifications": ["ISO9001", "ClimatePartner"],
    "independent_ratings": [
      {
        "source": "Trustpilot",
        "score": 4.6,
        "reviews": 12873,
        "url": "https://trustpilot.com/..."
      }
    ],
    "csat": 0.87,
    "nps": 54,
    "return_rate": 0.11,
    "service_sla": {
      "first_response_hours": 4,
      "resolution_hours_p50": 24
    },
    "unique_value_props": [
      "Lifetime repair service",
      "Local production",
      "Open spare parts catalog"
    ],
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
  }
}
```

### Catalog Product

Complete product representation with experiences, trust signals, and intent mapping.

```json
{
  "product": {
    "id": "sku_123",
    "parent_id": null,
    "title": "Classic High Top Sneaker Red",
    "short_desc": "Retro look, durable sole",
    "tech_specs": {
      "material": "Leather",
      "weight_grams": 420,
      "sizes": ["41", "42", "43", "44"],
      "care": "Hand wash, no dryer"
    },
    "price": {
      "currency": "EUR",
      "value": 129.90
    },
    "availability": {
      "state": "in_stock",
      "quantity": 220
    },
    "media": {
      "images": [
        {
          "url": "https://cdn.demo.shop/img/sneaker_red_1.jpg",
          "machine_captions": [
            {
              "lang": "en",
              "text": "Red high top sneaker on wood floor"
            }
          ],
          "embeddings": {
            "clip": {
              "dim": 768,
              "vector": "base64float..."
            }
          }
        }
      ],
      "documents": [
        {
          "url": "https://cdn.demo.shop/docs/sneaker_red_specs.pdf",
          "semantic_summary": {
            "lang": "en",
            "text": "Care guide and sizing chart with material specifications"
          },
          "checksum_sha256": "abc123..."
        }
      ]
    },
    "experiences": {
      "capsules": [
        {
          "id": "cap_sneaker_3d",
          "title": "3D configurator",
          "capsule_uri": "axp://capsules/cap_sneaker_3d.zip",
          "modality": "canvas3d",
          "preferred_size": {
            "width": 720,
            "height": 480
          },
          "params_schema": {
            "type": "object",
            "properties": {
              "color": {
                "enum": ["red", "black", "white"]
              },
              "size": {
                "type": "string"
              }
            },
            "required": ["color"]
          }
        }
      ],
      "demo_videos": [
        {
          "url": "https://cdn.demo.shop/vids/sneaker_walk.mp4",
          "caption": "On foot walking demo"
        }
      ]
    },
    "soft_signals": {
      "uniqueness_score": 0.82,
      "craftsmanship_score": 0.76,
      "sustainability_score": 0.61,
      "innovation_score": 0.55,
      "evidence": [
        {
          "kind": "certification",
          "name": "Leather Working Group",
          "url": "https://leatherworkinggroup.com/cert/abc"
        },
        {
          "kind": "award",
          "name": "Design Award 2024",
          "url": "https://designaward.com/2024/winners"
        }
      ]
    },
    "trust_signals": {
      "review_summary": {
        "avg_rating": 4.5,
        "count_total": 1342,
        "top_positive": ["Comfort", "Looks"],
        "top_negative": ["Runs small"]
      },
      "return_reasons": [
        {
          "reason": "size_issue",
          "share": 0.56
        },
        {
          "reason": "color_mismatch",
          "share": 0.18
        }
      ],
      "return_rate": 0.14,
      "warranty_days": 365
    },
    "intent_signals": [
      {
        "intent": "daily_commute",
        "share": 0.34
      },
      {
        "intent": "basketball",
        "share": 0.28
      },
      {
        "intent": "fashion",
        "share": 0.38
      }
    ],
    "policies": {
      "shipping": {
        "regions": ["DE", "AT", "NL"],
        "days": 2
      },
      "returns": {
        "days": 30,
        "restocking_fee": 0.0
      }
    },
    "provenance": {
      "brand_id": "brand_001",
      "last_verified": "2025-09-18T08:30:00Z",
      "signature": "base64url..."
    }
  }
}
```

### Ratings and Reviews

Normalized review format for agent-optimized ranking.

```json
{
  "product_id": "sku_123",
  "source": "Trustpilot",
  "rating": 5,
  "title": "Great fit",
  "text": "Comfortable for city walks, excellent build quality",
  "lang": "en",
  "verified_purchase": true,
  "timestamp": "2025-08-31T10:13:00Z",
  "aspects": {
    "comfort": 0.9,
    "build": 0.8,
    "style": 0.85
  }
}
```

## Export Format

AXP exports are distributed as signed ZIP bundles with the following structure:

```
axp_bundle.zip
├── manifest.json
├── brand_profile.json
├── catalog_products.jsonl
├── experiences.jsonl
├── policies.json
├── ratings_reviews.jsonl
├── assets/
│   ├── images/...
│   └── capsules/...
```

### Manifest Structure

```json
{
  "spec": "axp",
  "version": "0.1.0",
  "publisher": {
    "name": "Shopware Demo Store",
    "domain": "demo.shop",
    "public_keys": ["did:web:demo.shop#axp"]
  },
  "brand_profile": "brand_profile.json",
  "files": {
    "catalog_products": "catalog_products.jsonl",
    "experiences": "experiences.jsonl",
    "policies": "policies.json",
    "ratings_reviews": "ratings_reviews.jsonl"
  },
  "generated_at": "2025-09-18T10:00:00Z",
  "signature": {
    "alg": "RS256",
    "value": "base64url..."
  }
}
```

## MCP Protocol

### Tool: axp.getBrandProfile

Retrieves complete brand profile with trust signals.

**Input:**
```json
{}
```

**Output:**
Complete BrandProfile object

### Tool: axp.searchCatalog

Search products with rich filtering on soft signals.

**Input:**
```json
{
  "query": "sneakers",
  "filters": {
    "price": {
      "min": 0,
      "max": 500
    },
    "availability": ["in_stock", "preorder"],
    "intent": ["fashion", "daily_commute"],
    "soft_min": {
      "uniqueness_score": 0.5,
      "sustainability_score": 0.6
    }
  },
  "limit": 20,
  "cursor": "optional_pagination_cursor"
}
```

**Output:**
```json
{
  "items": [/* array of Product cards */],
  "next_cursor": "optional_next_page"
}
```

### Tool: axp.getProduct

Retrieve complete product details.

**Input:**
```json
{
  "product_id": "sku_123"
}
```

**Output:**
Complete Product object with all details

### Tool: axp.getExport

Download complete catalog as signed bundle.

**Input:**
```json
{
  "since": "2025-09-01T00:00:00Z"
}
```

**Output:**
```json
{
  "bundle_uri": "axp://export/axp_bundle_2025_09_18.zip",
  "checksum_sha256": "abc123...",
  "expires_at": "2025-09-18T23:59:59Z"
}
```

### Tool: axp.getCapsule

Retrieve sandboxed experience capsule configuration.

**Input:**
```json
{
  "capsule_id": "cap_sneaker_3d"
}
```

**Output:**
```json
{
  "capsule_uri": "axp://capsules/cap_sneaker_3d.zip",
  "sandbox_embed": {
    "kind": "iframe",
    "policy": {
      "allow_scripts": true,
      "allow_forms": false,
      "allow_fullscreen": false
    },
    "preferred_size": {
      "width": 720,
      "height": 480
    }
  }
}
```

### Tool: axp.subscribeInventory (Optional)

Subscribe to real-time inventory updates.

**Input:**
```json
{
  "product_ids": ["sku_123", "sku_456"]
}
```

**Output:**
```json
{
  "subscription_id": "inv_abc",
  "ttl_seconds": 600
}
```

**Events:**
```json
{
  "type": "inventory_update",
  "product_id": "sku_123",
  "availability": {
    "state": "in_stock",
    "quantity": 205
  }
}
```

### Tool: axp.health

Check server health status.

**Input:**
```json
{}
```

**Output:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Experience Capsules

Interactive micro-experiences with strict sandboxing.

### Capsule Manifest

```json
{
  "id": "cap_sneaker_3d",
  "name": "3D configurator",
  "version": "0.1.0",
  "entry": {
    "html": "index.html"
  },
  "surfaces": ["canvas3d", "html"],
  "sandbox_policy": {
    "dom": true,
    "storage": "none",
    "network": {
      "allow": ["https://cdn.demo.shop/assets/"],
      "block_all_others": true
    },
    "lifetime_seconds": 600,
    "permissions": []
  },
  "api": {
    "inbound_events": ["init", "configure", "set_variant", "request_quote"],
    "outbound_events": ["ready", "state_changed", "add_to_cart", "telemetry"]
  },
  "signature": "base64url..."
}
```

### PostMessage Contract

**MUST**: All inbound events carry `correlationId`, outbound events echo same id
**MUST**: Errors result in `{ type: "error", code: string, message: string, correlationId: string }`
**MUST**: Telemetry contains `event`, `ts`, `dur`, `surface`, `fps` (optional)
**SHOULD**: Host terminates capsule after `lifetime_seconds`
**MAY**: Support streaming mode for large model interactions

```typescript
// Inbound events (Host → Capsule)
type InboundEvent =
  | { type: "init"; correlationId: string }
  | { type: "configure"; correlationId: string; params: Record<string, unknown> }
  | { type: "set_variant"; correlationId: string; sku: string; params: Record<string, unknown> }
  | { type: "request_quote"; correlationId: string };

// Outbound events (Capsule → Host)
type OutboundEvent =
  | { type: "ready"; correlationId: string }
  | { type: "state_changed"; correlationId: string; state: Record<string, unknown> }
  | { type: "add_to_cart"; correlationId: string; sku: string; quantity: number }
  | { type: "telemetry"; correlationId: string; event: string; ts: string; dur?: number; data: Record<string, unknown> }
  | { type: "error"; correlationId: string; code: string; message: string };
```

## Security Model

### Content Security Policy

```
Content-Security-Policy:
  default-src 'none';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' https://cdn.demo.shop;
  connect-src https://cdn.demo.shop/assets/;
  frame-ancestors 'none';
```

### Sandbox Restrictions

1. **No Storage**: No cookies, localStorage, sessionStorage
2. **Limited Network**: Explicit allowlist only
3. **No Navigation**: Cannot change parent frame location
4. **Time-Limited**: Auto-terminate after TTL
5. **No Permissions**: No camera, microphone, geolocation

### Cryptographic Provenance

**MUST**: Apply replay protection via `X-AXP-Timestamp` header with max clock skew of 30 seconds for write operations
**MUST**: Support Proof-of-Work challenge for suspicious agents (optional enforcement)
**SHOULD**: Support mTLS for high-security scenarios
**SHOULD**: Maintain audit log with signature per entry and integrity verification

All top-level objects MUST support Ed25519 or RSA signatures with canonical JSON serialization.

## Controlled Vocabularies

### Return Reasons
- `size_issue`
- `damaged`
- `color_mismatch`
- `quality_expectation`
- `changed_mind`
- `shipping_delay`

### Customer Intent
- `gift`
- `daily_commute`
- `hobby`
- `professional_use`
- `travel`
- `fashion`

### Trust Badges
- `pci_dss_ready`
- `climate_partner`
- `fair_wear`
- `gdpr_controls`

### Evidence Kinds
- `certification`
- `award`
- `audit_report`
- `lab_test`
- `press_mention`

## Scoring Guidelines

### Normative Requirements

**MUST**: All scores in range [0,1] with evidence list
**MUST**: Time-weighting via exponential decay, standard half-life per signal class:
  - Behavioral signals: 90 days
  - Transaction signals: 180 days
  - Review signals: 365 days
**SHOULD**: Apply Dirichlet smoothing for sparse data
**MAY**: Use industry-specific benchmarks

### Agent Ranking Hints

```json
{
  "agent_ranking_hint": {
    "primary": ["uniqueness_score", "review_summary.avg_rating"],
    "secondary": ["return_rate", "sustainability_score"],
    "weights": {
      "uniqueness_score": 0.35,
      "review_summary.avg_rating": 0.25,
      "return_rate": 0.20,
      "sustainability_score": 0.20
    }
  }
}
```

## Internationalization

### Required Fields

**MUST**: Include for all products:
- `lang`: ISO 639-1 language code
- `currency`: ISO 4217 currency code
- `country_of_origin`: ISO 3166-1 alpha-2
- `tax_region`: Region identifier for tax calculation

**SHOULD**: Provide measurement units:
- `measurement_system`: "metric" or "imperial"
- Industry-specific: shoe sizes (EU/US/UK), textile weight (g/m²)

## Real-time Updates

### Subscription Events

**MUST**: Support these event types:
```json
{
  "inventory_update": { "previous_hash": "...", "new_hash": "...", "ts": "..." },
  "price_update": { "previous_hash": "...", "new_hash": "...", "ts": "..." },
  "availability_update": { "previous_hash": "...", "new_hash": "...", "ts": "..." },
  "trust_snapshot_update": { "previous_hash": "...", "new_hash": "...", "ts": "..." }
}
```

**SHOULD**: Use pull model with `since` cursor plus events with TTL
**MAY**: Implement `axp.subscribeInventory` for push notifications

## Rate Limits

Default limits per client:
- 600 requests per minute
- 50 concurrent connections
- 10MB max response size
- 100ms minimum interval between requests

## Error Handling

Standard HTTP status codes with AXP error format:

```json
{
  "error": {
    "code": "AXP_RATE_LIMIT",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 600,
      "window": "1m",
      "retry_after": 42
    }
  }
}
```

## AP2 Evidence Chain

### Required Evidence in AP2 Mandates

**MUST**: Merchants include in Cart Mandate:
- `axp_product_signature`: Product signature hash
- `axp_brand_profile_signature`: Brand profile signature hash

**SHOULD**: Include in `merchant_evidence`:
- `trust_score`: Normalized trust score [0,1]
- `review_summary`: Aggregated review metrics

**MAY**: Include in `experience_sessions`:
- `interaction_log_hash`: SHA-256 of interaction events
- `duration_seconds`: Total interaction time

### Mapping Table

| AXP Field | AP2 Field | Requirement |
|-----------|-----------|-------------|
| `product.id` | `displayItem.sku` | MUST |
| `price` | `amount` | MUST |
| `brand_profile_signature` | `merchant_evidence` | MUST |
| `intent_signals` | `intent_context` | SHOULD |
| `return_rate` | `risk_data` | SHOULD |
| `experience_proofs` | `interaction_evidence` | MAY |

## Compliance Suite

### Validation Tools

**MUST** provide:
- `axp validate schemas`: JSON Schema validation via AJV and Pydantic
- `axp sign`: Create canonical signature
- `axp verify`: Verify signature and canonicalization

**SHOULD** provide:
- `axp conformance`: Test suite with:
  - 10 golden test vectors
  - 2 edge cases
  - 1 invalid case
- Demo bundles and replay scripts

### Test Vectors

Reference implementation MUST pass all test vectors in `/tests/conformance/`:
- `golden/*.json`: Valid AXP documents with signatures
- `edge/*.json`: Edge cases (empty arrays, Unicode, large numbers)
- `invalid/*.json`: Documents that MUST fail validation

---

*This specification is a living document. Version 0.1.0 - Last updated: 2025-09-18*
*Developed as part of the [Agentic Commerce Organization](https://agentic-commerce.org/)*
