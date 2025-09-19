# AXP Implementation Guide

## Quick Start for Merchants

### 1. Minimum Requirements (MUST)

To be AXP compliant, you MUST provide:

```json
{
  "spec": "axp",
  "version": "0.1.0",
  "generated_at": "2025-09-18T10:00:00Z",
  "product": {
    "id": "your_sku",
    "title": "Product Name",
    "price": { "currency": "EUR", "value": 99.99 },
    "availability": { "state": "in_stock" },
    "lang": "en",
    "currency": "EUR",
    "country_of_origin": "DE",
    "tax_region": "EU"
  }
}
```

### 2. For AP2 Integration (MUST)

Include these signatures in your AP2 cart mandates:

```json
{
  "axp_evidence": {
    "axp_product_signature": "sha256:...",
    "axp_brand_profile_signature": "sha256:..."
  }
}
```

### 3. Enhanced Trust (SHOULD)

Add these fields to increase agent confidence:

```json
{
  "product": {
    "agent_ranking_hint": {
      "primary": ["review_rating", "return_rate"],
      "weights": {
        "review_rating": 0.6,
        "return_rate": 0.4
      }
    },
    "trust_signals": {
      "review_summary": {
        "avg_rating": 4.5,
        "count_total": 1342
      },
      "return_rate": 0.14
    }
  }
}
```

## Quick Start for Agents

### 1. Validate Signatures

Always verify AXP signatures before trusting data:

```javascript
const validator = new AXPValidator();
const isValid = await validator.verifySignature(product);
if (!isValid) throw new Error("Invalid product signature");
```

### 2. Check Evidence in AP2

When processing AP2 mandates, verify AXP evidence:

```javascript
const cart = await ap2.getCartMandate();
if (!cart.axp_evidence?.axp_product_signature) {
  console.warn("Missing AXP evidence - reduced trust");
}
```

### 3. Use Ranking Hints

Leverage merchant-provided ranking hints:

```javascript
const products = await axp.searchCatalog({ query: "sneakers" });
products.sort((a, b) => {
  const hint = a.agent_ranking_hint;
  if (!hint) return 0;
  
  // Use primary factors with weights
  const scoreA = calculateScore(a, hint.primary, hint.weights);
  const scoreB = calculateScore(b, hint.primary, hint.weights);
  return scoreB - scoreA;
});
```

## Normative Compliance Checklist

### Core Requirements (MUST)
- [ ] All documents include `spec`, `version`, `generated_at`
- [ ] Timestamps use ISO 8601 with Z suffix
- [ ] Canonical JSON serialization for signatures
- [ ] Support Ed25519 or RS256 signatures
- [ ] Include AXP evidence in AP2 mandates

### Recommended Features (SHOULD)
- [ ] Implement agent_ranking_hint
- [ ] Provide trust_score and review_summary
- [ ] Include internationalization fields
- [ ] Support real-time inventory updates
- [ ] Rotate signing keys quarterly

### Optional Enhancements (MAY)
- [ ] Experience capsules with sandbox policies
- [ ] On-chain signature anchoring
- [ ] Streaming mode for large catalogs
- [ ] Experience proof recording

## Integration Patterns

### Pattern 1: Shopware to AXP Export

```bash
# Generate AXP bundle from Shopware
php bin/console axp:export --format=bundle

# Validate the bundle
npm run test:conformance export/axp_bundle.zip

# Serve via MCP
npm run server:start -- --bundle export/axp_bundle.zip
```

### Pattern 2: Real-time Sync

```javascript
// Subscribe to inventory changes
const subscription = await axp.subscribeInventory({
  product_ids: ["sku_123", "sku_456"]
});

// Handle updates
subscription.on('inventory_update', (event) => {
  console.log(`Product ${event.product_id}: ${event.availability.quantity} in stock`);
});
```

### Pattern 3: Experience Capsules

```html
<!-- Embed sandboxed experience -->
<iframe 
  src="axp://capsules/sneaker_3d"
  sandbox="allow-scripts allow-same-origin"
  csp="script-src 'self'; connect-src https://cdn.shop.com">
</iframe>

<script>
// Communicate with capsule
window.addEventListener('message', (event) => {
  if (event.data.type === 'add_to_cart') {
    addToCart(event.data.sku, event.data.quantity);
  }
});

// Send configuration
iframe.contentWindow.postMessage({
  type: 'configure',
  correlationId: 'config_123',
  params: { color: 'red', size: '42' }
}, '*');
</script>
```

## Validation and Testing

### 1. Schema Validation

```bash
# Validate your product catalog
npm run test:schemas products.jsonl

# Check specific document
node scripts/validate.js product.json
```

### 2. Signature Verification

```bash
# Sign a document
axp sign --key private.pem --input product.json --output product.signed.json

# Verify signature
axp verify --key public.pem --input product.signed.json
```

### 3. Conformance Testing

```bash
# Run full conformance suite
npm run test:conformance

# Expected output:
# ✅ Golden: 10 passed, 0 failed
# ✅ Edge: 2 passed, 0 failed  
# ✅ Invalid: 1 correctly rejected, 0 incorrectly accepted
```

## Common Issues and Solutions

### Issue: Signature verification fails

**Solution**: Ensure canonical JSON serialization:
- Sort keys lexicographically
- Use Z suffix for timestamps
- Remove signature field before signing
- Normalize Unicode to NFC

### Issue: Low trust scores from agents

**Solution**: Provide more evidence:
- Add verified reviews
- Include certifications
- Provide historical metrics
- Add experience capsules

### Issue: AP2 transactions rejected

**Solution**: Include required AXP evidence:
- Add product and brand signatures
- Include trust_score
- Provide return_rate for risk assessment

## Support and Resources

- **Specification**: [SPECIFICATION.md](docs/SPECIFICATION.md)
- **AP2 Integration**: [AP2_INTEGRATION.md](docs/AP2_INTEGRATION.md)  
- **Security Guide**: [SECURITY.md](docs/SECURITY.md)
- **Community**: [agentic-commerce.org](https://agentic-commerce.org/)

---

*This guide is part of the AXP v0.1.0 specification developed by the [Agentic Commerce Organization](https://agentic-commerce.org/).*
