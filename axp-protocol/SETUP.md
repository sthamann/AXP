# AXP Protocol - Quick Setup Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites

Ensure you have the following installed:
- **Node.js** (v18 or higher)
- **npm** (comes with Node.js)
- **Git**

Check versions:
```bash
node --version  # Should be v18.x.x or higher
npm --version   # Should be v8.x.x or higher
git --version   # Any recent version
```

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/agentic-commerce/axp-protocol.git
cd axp-protocol

# Install dependencies
npm install
```

### 2. Start the MCP Server

In one terminal window:
```bash
npm run server:start
```

You should see:
```
AXP MCP Server running on stdio
```

### 3. Run the Interactive Demo

In another terminal window:
```bash
npm run demo:client
```

This will launch an interactive CLI where you can:
- Browse brand profiles
- Search products
- View product details
- Explore experience capsules
- Test advanced searches

### 4. Test the API

Try these example commands in the demo client:

1. **Get Brand Profile** - Option 1
2. **Search Products** - Option 2, then enter "sneaker"
3. **Get Product Details** - Option 3, then enter "sku_123"
4. **Explore Capsule** - Option 4, then enter "cap_sneaker_3d"

## 📦 Creating Your First Bundle

Generate an AXP export bundle:

```bash
npm run bundle:example
```

This creates a signed bundle in `exports/` containing:
- Brand profile
- Product catalog
- Reviews & ratings
- Experience capsules
- Policies

## 🔧 Development Setup

### TypeScript Development

```bash
# Watch mode for TypeScript
npm run build:watch

# Run development server with auto-reload
npm run server:dev
```

### Python Integration

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Python examples
python examples/python/client.py
```

### Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Validate schemas
npm run validate:schemas
```

## 🎮 Creating a Custom Experience Capsule

1. **Create capsule directory:**
```bash
mkdir examples/capsules/my-capsule
cd examples/capsules/my-capsule
```

2. **Create manifest.json:**
```json
{
  "id": "cap_my_experience",
  "name": "My Experience",
  "version": "0.1.0",
  "entry": {
    "html": "index.html"
  },
  "surfaces": ["html"],
  "sandbox_policy": {
    "dom": true,
    "storage": "none",
    "network": {
      "allow": [],
      "block_all_others": true
    },
    "lifetime_seconds": 600,
    "permissions": []
  },
  "api": {
    "inbound_events": ["init", "configure"],
    "outbound_events": ["ready", "state_changed"]
  }
}
```

3. **Create index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>My AXP Capsule</title>
</head>
<body>
    <h1>My Experience</h1>
    <script>
        // Listen for messages from parent
        window.addEventListener('message', (event) => {
            if (event.data.type === 'init') {
                // Send ready signal
                window.parent.postMessage({
                    type: 'ready'
                }, '*');
            }
        });
    </script>
</body>
</html>
```

## 🔗 Integration Examples

### Node.js/TypeScript Client

```typescript
import { AXPClient } from './src/client';

const client = new AXPClient({
  serverUrl: 'http://localhost:3000'
});

// Search for sustainable products
const results = await client.searchCatalog({
  filters: {
    soft_min: {
      sustainability_score: 0.7
    }
  }
});

console.log(`Found ${results.items.length} sustainable products`);
```

### Python Client

```python
from axp_protocol import AXPClient

client = AXPClient("http://localhost:3000")

# Get brand profile
brand = client.get_brand_profile()
print(f"Brand: {brand.brand.legal_name}")

# Search products
products = client.search_catalog(
    filters={"soft_min": {"uniqueness_score": 0.8}}
)

for product in products.items:
    print(f"- {product.title}: €{product.price.value}")
```

### MCP Direct Usage

```bash
# Using the MCP CLI directly
echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "axp.getBrandProfile", "arguments": {}}, "id": 1}' | npm run server:start
```

## 🐳 Docker Setup (Optional)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "run", "server:start"]
```

Build and run:
```bash
docker build -t axp-server .
docker run -p 3000:3000 axp-server
```

## 📱 Frontend Integration

### React Example

```jsx
import { useState, useEffect } from 'react';
import { AXPClient } from '@agentic-commerce/axp-protocol';

function ProductList() {
  const [products, setProducts] = useState([]);
  const client = new AXPClient({ serverUrl: '/api/axp' });

  useEffect(() => {
    client.searchCatalog({ limit: 10 })
      .then(result => setProducts(result.items));
  }, []);

  return (
    <div>
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

### Embedding Capsules

```html
<!-- Embed an experience capsule -->
<iframe
  id="capsule"
  src="capsule.html"
  sandbox="allow-scripts allow-same-origin"
  style="width: 720px; height: 480px; border: none;"
></iframe>

<script>
  // Setup message bridge
  const capsule = document.getElementById('capsule');
  
  capsule.addEventListener('load', () => {
    capsule.contentWindow.postMessage({
      type: 'init',
      correlationId: '12345'
    }, '*');
  });
  
  window.addEventListener('message', (event) => {
    if (event.source === capsule.contentWindow) {
      if (event.data.type === 'add_to_cart') {
        // Handle add to cart
        console.log('Add to cart:', event.data);
      }
    }
  });
</script>
```

## 🛠️ Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is in use
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or use a different port
export PORT=3001 && npm run server:start
```

**Module not found errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Schema validation failing:**
```bash
# Validate individual schemas
npx ajv compile -s schemas/axp/product.schema.json
```

**TypeScript errors:**
```bash
# Regenerate types
npm run generate:types
```

## 📚 Next Steps

1. **Read the Specification**: [docs/SPECIFICATION.md](docs/SPECIFICATION.md)
2. **Understand Security**: [docs/SECURITY.md](docs/SECURITY.md)
3. **Integration Guide**: [docs/INTEGRATION.md](docs/INTEGRATION.md)
4. **Contributing**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 💬 Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/agentic-commerce/axp-protocol/issues)
- **Discussions**: [Ask questions](https://github.com/agentic-commerce/axp-protocol/discussions)
- **Discord**: [Join our community](https://discord.gg/agentic-commerce)

---

Ready to build amazing agentic commerce experiences? Let's go! 🚀
