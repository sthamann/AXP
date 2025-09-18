# Changelog

All notable changes to the AXP Protocol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [0.1.0] - 2025-09-18

### Added
- Initial release of AXP Protocol
- Core data models:
  - Brand Profile with trust signals
  - Product catalog with soft signals
  - Review aggregation
  - Experience Capsules
  - Export bundles
- MCP Tools:
  - `axp.getBrandProfile` - Retrieve brand information
  - `axp.searchCatalog` - Search with soft signal filtering  
  - `axp.getProduct` - Get detailed product data
  - `axp.getExport` - Download signed bundles
  - `axp.getCapsule` - Retrieve experience configurations
  - `axp.subscribeInventory` - Real-time inventory updates
  - `axp.health` - Server health check
- Scoring system:
  - Uniqueness score
  - Craftsmanship score
  - Sustainability score
  - Innovation score
- PostMessage API for capsule communication
- Controlled vocabularies for standardization
- GDPR-compliant privacy model (no PII)
- Multi-language support

### Known Issues
- Capsule resource monitoring is conceptual (browser limitations)
- Inventory subscriptions not fully implemented
- Mock signatures (real crypto implementation needed for production)

## Roadmap

### [0.2.0] - Planned
- [ ] Advanced capsule modalities (AR, VR)
- [ ] Real-time collaborative experiences
- [ ] Enhanced AI agent hints
- [ ] GraphQL API support
- [ ] WebAssembly capsule support

### [0.3.0] - Planned
- [ ] Federated brand networks
- [ ] Cross-merchant experience sharing
- [ ] Blockchain provenance option
- [ ] Advanced analytics dashboard

### [0.4.0] - Planned
- [ ] Cross-agent experience state
- [ ] Multi-party capsule interactions
- [ ] Dynamic pricing signals
- [ ] B2B extension

### [1.0.0] - Planned
- [ ] Production-ready release
- [ ] Certification program
- [ ] Reference implementations in multiple languages
- [ ] Enterprise features
- [ ] SLA guarantees

---

For more details on upcoming features, see our [GitHub Issues](https://github.com/agentic-commerce/axp-protocol/issues).
