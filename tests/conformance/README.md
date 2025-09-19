# AXP Conformance Test Suite

This directory contains the official AXP protocol conformance test suite with test vectors for validation.

## Structure

- `golden/` - Valid AXP documents with canonical signatures
- `edge/` - Edge cases (empty arrays, Unicode, large numbers)
- `invalid/` - Documents that MUST fail validation

## Test Vectors

### Golden Vectors (10 test cases)
1. `product_basic.json` - Minimal valid product
2. `product_complete.json` - Product with all optional fields
3. `product_with_variants.json` - Product with variant matrix
4. `product_with_capsule.json` - Product with experience capsule
5. `brand_profile_basic.json` - Minimal valid brand profile
6. `brand_profile_complete.json` - Brand with all trust factors
7. `review_verified.json` - Verified purchase review
8. `bundle_manifest.json` - Valid export bundle manifest
9. `signed_product.json` - Product with valid EdDSA signature
10. `ap2_evidence.json` - Complete AP2 evidence chain

### Edge Cases (2 test cases)
1. `unicode_product.json` - Product with Unicode characters (emoji, CJK, RTL)
2. `boundary_values.json` - Edge values (max/min numbers, empty arrays)

### Invalid Cases (1 test case)
1. `malformed_signature.json` - Invalid signature format (MUST fail)

## Running Tests

```bash
# Validate schemas
npm run test:schemas

# Check signatures
npm run test:signatures

# Full conformance check
npm run test:conformance
```

## Validation Rules

All test vectors MUST:
1. Pass JSON Schema validation
2. Follow canonical JSON serialization
3. Include required timestamps in ISO 8601 with Z suffix
4. Have valid signatures (for signed documents)

## Reference Implementation

See `scripts/validate.js` for the reference implementation.
