# AXP Integration Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Platform Integration](#platform-integration)
3. [Agent Integration](#agent-integration)
4. [Experience Capsules](#experience-capsules)
5. [Security Implementation](#security-implementation)
6. [Testing](#testing)
7. [Production Checklist](#production-checklist)

## Quick Start

### Installation

```bash
# Install AXP Protocol
npm install @agentic-commerce/axp-protocol

# Or with Python
pip install axp-protocol
```

### Basic Setup (TypeScript)

```typescript
import { AXPClient, Product, BrandProfile } from '@agentic-commerce/axp-protocol';

// Initialize client
const client = new AXPClient({
  endpoint: 'https://api.yourstore.com/axp',
  apiKey: process.env.AXP_API_KEY
});

// Get brand profile
const brand = await client.getBrandProfile();

// Search products
const results = await client.searchCatalog({
  query: 'sneakers',
  filters: {
    soft_min: {
      sustainability_score: 0.7
    }
  }
});
```

### Basic Setup (Python)

```python
from axp_protocol import AXPClient
from axp_protocol.models import SearchFilters, SoftMinFilters

# Initialize client
client = AXPClient(
    endpoint="https://api.yourstore.com/axp",
    api_key=os.environ["AXP_API_KEY"]
)

# Get brand profile
brand = client.get_brand_profile()

# Search products
results = client.search_catalog(
    query="sneakers",
    filters=SearchFilters(
        soft_min=SoftMinFilters(sustainability_score=0.7)
    )
)
```

## Platform Integration

### Implementing AXP as a Commerce Platform

#### 1. Data Preparation

Transform your existing product catalog to AXP format:

```typescript
// Example transformation
function transformToAXP(product: YourProduct): Product {
  return {
    id: product.sku,
    title: product.name,
    price: {
      currency: product.currency,
      value: product.price
    },
    availability: {
      state: product.stock > 0 ? "in_stock" : "out_of_stock",
      quantity: product.stock
    },
    soft_signals: calculateSoftSignals(product),
    trust_signals: aggregateTrustSignals(product),
    // ... more fields
  };
}

function calculateSoftSignals(product: YourProduct) {
  return {
    uniqueness_score: calculateUniqueness(product),
    sustainability_score: calculateSustainability(product),
    craftsmanship_score: calculateCraftsmanship(product),
    innovation_score: calculateInnovation(product),
    evidence: gatherEvidence(product)
  };
}
```

#### 2. MCP Server Implementation

```typescript
import { Server } from "@modelcontextprotocol/sdk/server";
import { AXPTools } from '@agentic-commerce/axp-protocol';

class YourAXPServer {
  private axpTools: AXPTools;
  
  constructor(dataSource: YourDataSource) {
    this.axpTools = new AXPTools(dataSource);
  }

  async handleSearchCatalog(params: SearchCatalogInput) {
    // Apply your business logic
    const products = await this.dataSource.search(params);
    
    // Apply AXP scoring
    const scored = this.applyRanking(products, params.filters?.soft_min);
    
    return {
      items: scored,
      next_cursor: this.generateCursor(params)
    };
  }

  private applyRanking(products: Product[], softMin?: SoftMinFilters) {
    return products
      .filter(p => this.meetsSoftRequirements(p, softMin))
      .sort((a, b) => this.rankProducts(a, b));
  }
}
```

#### 3. Export Bundle Generation

```typescript
import { createWriteStream } from 'fs';
import * as archiver from 'archiver';
import { sign } from 'jsonwebtoken';

async function generateExportBundle(): Promise<string> {
  const archive = archiver('zip', { zlib: { level: 9 }});
  const output = createWriteStream('axp_bundle.zip');
  
  archive.pipe(output);
  
  // Add manifest
  const manifest = {
    spec: "axp",
    version: "0.1.0",
    publisher: {
      name: "Your Store",
      domain: "yourstore.com",
      public_keys: ["did:web:yourstore.com#axp"]
    },
    files: {
      catalog_products: "catalog_products.jsonl",
      ratings_reviews: "ratings_reviews.jsonl"
    },
    generated_at: new Date().toISOString(),
    signature: generateSignature(manifestData)
  };
  
  archive.append(JSON.stringify(manifest, null, 2), { name: 'manifest.json' });
  
  // Add product data
  for await (const product of streamProducts()) {
    archive.append(JSON.stringify(product) + '\n', { name: 'catalog_products.jsonl' });
  }
  
  await archive.finalize();
  return 'axp_bundle.zip';
}
```

## Agent Integration

### Building an AXP-Aware Agent

#### 1. Discovery Phase

```typescript
class ShoppingAgent {
  private axpClient: AXPClient;
  
  async discoverProducts(userIntent: string) {
    // Parse user intent
    const { keywords, preferences } = this.parseIntent(userIntent);
    
    // Search with soft signals
    const results = await this.axpClient.searchCatalog({
      query: keywords,
      filters: {
        soft_min: this.mapPreferencesToScores(preferences),
        intent: this.detectIntentTypes(userIntent)
      }
    });
    
    // Rank based on agent_ranking_hint
    return this.applyAgentRanking(results.items);
  }
  
  private applyAgentRanking(products: Product[]) {
    return products.map(p => {
      const score = this.calculateScore(p, p.agent_ranking_hint);
      return { ...p, agent_score: score };
    }).sort((a, b) => b.agent_score - a.agent_score);
  }
}
```

#### 2. Experience Integration

```typescript
class ExperienceRenderer {
  async renderCapsule(capsuleId: string): Promise<HTMLIFrameElement> {
    // Get capsule configuration
    const capsule = await this.axpClient.getCapsule(capsuleId);
    
    // Create sandboxed iframe
    const iframe = document.createElement('iframe');
    iframe.src = capsule.capsule_uri;
    iframe.sandbox.add('allow-scripts', 'allow-same-origin');
    
    // Apply security policy
    this.applySandboxPolicy(iframe, capsule.sandbox_embed.policy);
    
    // Setup message bridge
    this.setupMessageBridge(iframe);
    
    return iframe;
  }
  
  private setupMessageBridge(iframe: HTMLIFrameElement) {
    window.addEventListener('message', (event) => {
      // Validate origin
      if (!this.isValidOrigin(event.origin)) return;
      
      // Handle capsule events
      switch(event.data.type) {
        case 'add_to_cart':
          this.handleAddToCart(event.data);
          break;
        case 'state_changed':
          this.handleStateChange(event.data);
          break;
        // ... more handlers
      }
    });
  }
}
```

## Experience Capsules

### Creating a Capsule

#### 1. Capsule Structure

```
my-capsule/
├── manifest.json
├── index.html
├── app.js
├── styles.css
└── assets/
    └── models/
```

#### 2. Implementing PostMessage API

```javascript
// capsule.js
class CapsuleController {
  constructor() {
    this.state = {};
    this.setupAPI();
  }
  
  setupAPI() {
    window.addEventListener('message', (event) => {
      const { type, ...params } = event.data;
      
      switch(type) {
        case 'init':
          this.initialize(params);
          break;
        case 'configure':
          this.configure(params);
          break;
        // Handle all required events
      }
    });
  }
  
  sendMessage(message) {
    window.parent.postMessage(message, '*');
  }
  
  initialize({ correlationId }) {
    // Initialize your capsule
    this.sendMessage({ type: 'ready', correlationId });
  }
  
  configure(params) {
    // Apply configuration
    Object.assign(this.state, params);
    this.render();
    this.sendMessage({ 
      type: 'state_changed', 
      state: this.state 
    });
  }
}
```

#### 3. Sandbox Compliance

```javascript
// Ensure compliance with sandbox policy
const ALLOWED_ENDPOINTS = [
  'https://cdn.yourstore.com/assets/'
];

async function fetchAsset(url) {
  // Validate URL against allowed endpoints
  if (!ALLOWED_ENDPOINTS.some(endpoint => url.startsWith(endpoint))) {
    throw new Error('Endpoint not allowed by sandbox policy');
  }
  
  return fetch(url);
}

// No local storage
// Use in-memory state only
const state = new Map();

// Auto-cleanup on timeout
setTimeout(() => {
  cleanup();
  window.parent.postMessage({ type: 'capsule_timeout' }, '*');
}, 600000); // 10 minutes as specified in policy
```

## Security Implementation

### 1. Signature Verification

```typescript
import { verify } from 'jsonwebtoken';
import { createVerify } from 'crypto';

class SignatureVerifier {
  async verifyBrandProfile(profile: BrandProfile): Promise<boolean> {
    if (!profile.signature) return false;
    
    const publicKey = await this.fetchPublicKey(profile.brand.id);
    
    try {
      const payload = this.canonicalize(profile);
      return verify(profile.signature.value, publicKey, {
        algorithms: [profile.signature.alg]
      });
    } catch {
      return false;
    }
  }
  
  private canonicalize(data: any): string {
    // Remove signature field and canonicalize
    const { signature, ...payload } = data;
    return JSON.stringify(payload, Object.keys(payload).sort());
  }
}
```

### 2. Capsule Sandboxing

```typescript
class CapsuleSandbox {
  createSecureFrame(capsule: ExperienceCapsule): HTMLIFrameElement {
    const frame = document.createElement('iframe');
    
    // Apply CSP
    frame.setAttribute('csp', this.generateCSP(capsule.sandbox_policy));
    
    // Set sandbox attributes
    const sandboxAttrs = [];
    if (capsule.sandbox_policy.dom) {
      sandboxAttrs.push('allow-scripts');
    }
    if (capsule.sandbox_policy.permissions?.includes('camera')) {
      frame.allow = 'camera';
    }
    
    frame.sandbox = sandboxAttrs.join(' ');
    
    // Resource limits (conceptual - actual implementation varies)
    this.applyResourceLimits(frame, capsule.resources);
    
    return frame;
  }
  
  private generateCSP(policy: SandboxPolicy): string {
    const directives = [
      "default-src 'none'",
      "script-src 'self'",
      "style-src 'self' 'unsafe-inline'",
    ];
    
    if (policy.network.allow) {
      directives.push(`connect-src ${policy.network.allow.join(' ')}`);
    }
    
    return directives.join('; ');
  }
}
```

## Testing

### Unit Tests

```typescript
// axp.test.ts
import { validateProduct, calculateSoftSignals } from '@agentic-commerce/axp-protocol';

describe('AXP Product Validation', () => {
  test('validates required fields', () => {
    const product = {
      id: 'test_123',
      title: 'Test Product',
      price: { currency: 'EUR', value: 99.99 },
      availability: { state: 'in_stock' }
    };
    
    expect(validateProduct(product)).toBe(true);
  });
  
  test('calculates soft signals correctly', () => {
    const signals = calculateSoftSignals(testProduct);
    
    expect(signals.uniqueness_score).toBeGreaterThanOrEqual(0);
    expect(signals.uniqueness_score).toBeLessThanOrEqual(1);
    expect(signals.evidence).toHaveLength(greaterThan(0));
  });
});
```

### Integration Tests

```typescript
// integration.test.ts
describe('AXP MCP Server', () => {
  let server: AXPServer;
  
  beforeAll(async () => {
    server = new AXPServer(testConfig);
    await server.start();
  });
  
  test('searchCatalog returns valid results', async () => {
    const results = await server.tools.searchCatalog({
      query: 'test',
      limit: 10
    });
    
    expect(results.items).toBeInstanceOf(Array);
    results.items.forEach(item => {
      expect(validateProduct(item)).toBe(true);
    });
  });
  
  test('getCapsule enforces sandbox policy', async () => {
    const capsule = await server.tools.getCapsule({
      capsule_id: 'test_capsule'
    });
    
    expect(capsule.sandbox_embed.policy.allow_scripts).toBe(true);
    expect(capsule.sandbox_embed.policy.allow_fullscreen).toBe(false);
  });
});
```

## Production Checklist

### Before Launch

- [ ] **Data Quality**
  - [ ] All products have required fields
  - [ ] Soft signals are calculated and evidenced
  - [ ] Trust signals are aggregated from real data
  - [ ] Reviews are normalized and deduplicated

- [ ] **Security**
  - [ ] All data is signed with valid certificates
  - [ ] Capsules are properly sandboxed
  - [ ] Rate limiting is implemented
  - [ ] Input validation on all endpoints
  - [ ] No PII in exports

- [ ] **Performance**
  - [ ] Export bundles are compressed
  - [ ] Search queries are optimized
  - [ ] Capsules load within 2 seconds
  - [ ] API responds within 200ms p95

- [ ] **Compliance**
  - [ ] GDPR compliant (no PII)
  - [ ] Accessibility (WCAG 2.1 AA for capsules)
  - [ ] Multi-language support
  - [ ] Proper licensing

- [ ] **Monitoring**
  - [ ] API endpoint monitoring
  - [ ] Error tracking
  - [ ] Performance metrics
  - [ ] Usage analytics

### Post-Launch

- [ ] Monitor adoption metrics
- [ ] Gather agent feedback
- [ ] Track conversion improvements
- [ ] Measure return rate changes
- [ ] Update scoring algorithms based on data

## Support

For questions and support:
- GitHub Issues: [github.com/agentic-commerce/axp-protocol](https://github.com/agentic-commerce/axp-protocol)
- Community: [discord.gg/agentic-commerce](https://discord.gg/agentic-commerce)
- Email: support@agentic-commerce.org

---

*Last updated: 2025-09-18*
