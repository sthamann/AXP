# Changelog

All notable changes to the AXP Protocol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Major Protocol Enhancements

#### Schema Extensions
- **Brand Profile**: Added legal (VAT ID, EORI, DUNS, GLN), payments (methods, chargeback rate), fulfillment (carriers, on-time rate), compliance (WEEE, RoHS, REACH), and tech stack fields
- **Product Schema**: Added identifiers (GTIN, MPN), taxonomy (Google Product Category, HS Code), extended pricing (regional, unit price, MAP), shipping details, regulatory info, warranty, B2B features (MOQ, Incoterms), digital product support
- **Intent Signals**: Added measurement windows, sample sizes, confidence methods (Wilson score), and statistical validation
- **Experience Proofs**: Added cryptographic proof of customer interactions with capsules
- **Agent Ranking Hints**: Added weighted scoring system for AI optimization

#### Third-Party Integration
- Enrichment module for Trustpilot, Trusted Shops, Google Seller Ratings, and BuiltWith
- Anomaly detection for suspicious metric changes
- Verifiable Credentials generation for third-party evidence
- Provider-specific adapters with TTL and caching

#### AP2 Evidence Chain
- Public/sealed evidence separation (32KB/1MB limits)
- Value-based evidence requirements (<€100 optional, >€1000 mandatory)
- Encrypted sealed evidence for sensitive data
- Evidence retention and privacy policies

#### Normative Standards
- KPI formulas document with precise calculations
- Wilson score confidence intervals
- Time decay functions with λ values
- Dirichlet smoothing for sparse data
- Anomaly detection thresholds

#### MCP Tools Suite
- Extended 15+ tools for agent interaction
- `axp.searchCatalog` with advanced filtering
- `axp.getEnrichmentStatus` for data freshness
- `axp.calculateIntent` with confidence metrics
- `axp.validateCompliance` for regulatory checks
- `axp.getB2BTerms` with quantity-based pricing

#### Conformance Profiles
- Core Profile (mandatory minimum)
- Retail Profile (B2C features)
- B2B Profile (business transactions)
- Regulated Profile (compliance-heavy)
- Digital Profile (software/subscriptions)
- Marketplace Profile (multi-vendor)

### Added - Documentation
- Normative specification with MUST/SHOULD/CAN requirements
- Canonical JSON serialization rules
- KPI_FORMULAS.md with mathematical definitions
- PROFILES.md with conformance requirements
- AP2_EVIDENCE_CHAIN.md for payment integration
- Implementation guide with profile-specific examples
- Nike Shoe V2 3D Experience Capsule with USDZ model support
- Test harness for AXP Capsule development and debugging

### Updated
- README with big picture architecture diagram
- Integration with Google's AP2 (Agent Payments Protocol)
- All examples updated with new schema fields
- Enhanced 3D sneaker configurator with real model viewer implementation
- Migrated from canvas-based simulation to model-viewer 3.3.0
- Added Nike branding and premium visual design
- Implemented dynamic pricing based on colorway selection

### Security
- `last_verified` and `ttl_seconds` in all signed objects
- Well-known endpoints for JWKS and brand profiles
- Key rotation requirements (quarterly SHOULD)
- Replay protection with 30-second max clock skew

### Compliance
- Test suite with golden vectors, edge cases, and invalid cases
- Reference validator implementation
- Canonical JSON validation
- Profile-specific validation tools

## [0.1.0] - 2025-09-18

### Added
- Complete AXP v0.1.0 protocol specification
- JSON Schema definitions for all data objects
- TypeScript type definitions
- Python Pydantic models
- MCP server implementation with in-memory store
- Interactive demo client
- Example data (brand profile, products, reviews)
- Experience Capsule framework with sandboxing
- Example 3D sneaker configurator capsule
- Bundle generation script
- Comprehensive documentation
- Security model with cryptographic signatures
- Integration guide with code examples
- Contributing guidelines

### Security
- Implemented strict CSP for capsules
- Added signature verification for data integrity
- Sandboxed iframe execution for capsules
- Rate limiting on API endpoints


## Roadmap

### [0.2.0] - Planned Q1 2026
- [ ] Validator CLI for profile compliance
- [ ] Shopware 6.5+ export module
- [ ] WooCommerce plugin
- [ ] Real-time inventory sync via WebSocket
- [ ] Reference implementation in Go

### [0.3.0] - Planned Q2 2026
- [ ] Advanced capsule modalities (AR, VR)
- [ ] Federated trust network
- [ ] Cross-merchant experience sharing
- [ ] GraphQL API support
- [ ] WebAssembly capsule support

### [0.4.0] - Planned Q3 2026
- [ ] Blockchain anchoring for high-value transactions
- [ ] Multi-agent collaboration protocols
- [ ] Advanced analytics dashboard
- [ ] Dynamic pricing signals
- [ ] Cross-agent experience state

### [1.0.0] - Planned Q4 2026
- [ ] Production-ready release
- [ ] Certification program for merchants
- [ ] Reference implementations in 5+ languages
- [ ] Enterprise support packages
- [ ] SLA guarantees
- [ ] ISO standardization submission

---

For more details on upcoming features, see our [GitHub Issues](https://github.com/agentic-commerce/axp-protocol/issues).
