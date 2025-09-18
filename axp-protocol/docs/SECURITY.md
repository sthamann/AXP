# AXP Security Model

## Overview

The AXP protocol implements defense-in-depth security with focus on:
- **Data Integrity**: Cryptographic signatures ensure data authenticity
- **Privacy**: No PII exposure, GDPR compliant by design
- **Sandbox Isolation**: Experience capsules run in strict sandboxes
- **Trust Chain**: Verifiable provenance from brand to agent

## Threat Model

### Identified Threats

1. **Data Tampering**: Malicious modification of product/brand data
2. **Capsule Exploitation**: Malicious code in experience capsules
3. **Privacy Breach**: Exposure of customer PII
4. **Resource Exhaustion**: DoS via expensive operations
5. **Supply Chain Attacks**: Compromised dependencies

### Mitigation Strategies

| Threat | Mitigation | Implementation |
|--------|------------|----------------|
| Data Tampering | Cryptographic signatures | Ed25519/RSA signatures on all data |
| Capsule Exploitation | Strict sandboxing | CSP, iframe isolation, resource limits |
| Privacy Breach | Data minimization | No PII in protocol, anonymized analytics |
| Resource Exhaustion | Rate limiting | Per-client limits, query complexity bounds |
| Supply Chain | Dependency verification | Lock files, vulnerability scanning |

## Cryptographic Architecture

### Signature Scheme

```
┌─────────────┐     Signs      ┌──────────────┐
│   Brand     │ ─────────────> │  AXP Data    │
│  Private    │                 │   Bundle     │
│    Key      │                 └──────────────┘
└─────────────┘                        │
                                       │ Includes signature
                                       ▼
                               ┌──────────────┐
                               │   Agent      │
                               │  Verifies    │
                               │  with Public │
                               │     Key      │
                               └──────────────┘
```

### Key Management

```javascript
// Key generation (Ed25519 recommended)
const { publicKey, privateKey } = await generateKeyPair('ed25519');

// Key storage
// - Private keys: HSM or secure key management service
// - Public keys: Published via DID or well-known endpoint

// Key rotation
// - Annual rotation recommended
// - Maintain old keys for verification only
```

### Signature Generation

```typescript
import { sign } from 'tweetnacl';
import { encode } from 'base64url';

function signData(data: any, privateKey: Uint8Array): string {
  // 1. Canonicalize data (remove signature field)
  const { signature, ...payload } = data;
  
  // 2. Sort keys for deterministic JSON
  const canonical = JSON.stringify(payload, Object.keys(payload).sort());
  
  // 3. Sign the canonical form
  const signature = sign.detached(
    new TextEncoder().encode(canonical),
    privateKey
  );
  
  // 4. Return base64url encoded signature
  return encode(signature);
}
```

### Signature Verification

```typescript
import { sign } from 'tweetnacl';
import { decode } from 'base64url';

async function verifySignature(
  data: any,
  publicKeyId: string
): Promise<boolean> {
  // 1. Fetch public key
  const publicKey = await fetchPublicKey(publicKeyId);
  
  // 2. Extract and decode signature
  const signatureBytes = decode(data.signature.value);
  
  // 3. Canonicalize data
  const { signature, ...payload } = data;
  const canonical = JSON.stringify(payload, Object.keys(payload).sort());
  
  // 4. Verify
  return sign.detached.verify(
    new TextEncoder().encode(canonical),
    signatureBytes,
    publicKey
  );
}
```

## Capsule Sandboxing

### Security Boundaries

```
┌─────────────────────────────────────────────┐
│              Browser Context                 │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐    │
│  │        Parent Frame (Agent)         │    │
│  │  - Full permissions                 │    │
│  │  - Controls capsule lifecycle       │    │
│  └─────────────────────────────────────┘    │
│                    │                         │
│         PostMessage Bridge Only              │
│                    │                         │
│  ┌─────────────────────────────────────┐    │
│  │     Sandboxed iframe (Capsule)     │    │
│  │  - No cookies/storage               │    │
│  │  - Limited network (allowlist)      │    │
│  │  - No navigation                    │    │
│  │  - Time-limited execution           │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Content Security Policy

```http
Content-Security-Policy: 
  default-src 'none';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' https://cdn.allowed.com;
  connect-src https://api.allowed.com;
  frame-ancestors 'none';
  base-uri 'none';
  form-action 'none';
```

### Sandbox Attributes

```html
<iframe
  src="capsule.html"
  sandbox="allow-scripts allow-same-origin"
  allow="camera 'none'; microphone 'none'; geolocation 'none';"
  referrerpolicy="no-referrer"
  loading="lazy"
></iframe>
```

### Resource Limits

```javascript
// CPU throttling (conceptual)
class ResourceMonitor {
  constructor(iframe, limits) {
    this.iframe = iframe;
    this.limits = limits;
    this.startTime = Date.now();
  }
  
  checkLimits() {
    // Time limit
    if (Date.now() - this.startTime > this.limits.lifetime_seconds * 1000) {
      this.terminate('timeout');
    }
    
    // Memory monitoring (where available)
    if (performance.memory) {
      if (performance.memory.usedJSHeapSize > this.limits.max_memory_mb * 1024 * 1024) {
        this.terminate('memory_exceeded');
      }
    }
  }
  
  terminate(reason) {
    this.iframe.remove();
    console.log(`Capsule terminated: ${reason}`);
  }
}
```

## Network Security

### Rate Limiting

```typescript
class RateLimiter {
  private requests = new Map<string, number[]>();
  
  isAllowed(clientId: string): boolean {
    const now = Date.now();
    const minute = 60 * 1000;
    
    // Get requests in last minute
    const clientRequests = this.requests.get(clientId) || [];
    const recentRequests = clientRequests.filter(t => now - t < minute);
    
    // Check limit (600/minute default)
    if (recentRequests.length >= 600) {
      return false;
    }
    
    // Update and allow
    recentRequests.push(now);
    this.requests.set(clientId, recentRequests);
    return true;
  }
}
```

### Input Validation

```typescript
import { z } from 'zod';

// Strict input validation schemas
const SearchSchema = z.object({
  query: z.string().max(200).optional(),
  filters: z.object({
    price: z.object({
      min: z.number().min(0).max(1000000),
      max: z.number().min(0).max(1000000)
    }).optional()
  }).optional(),
  limit: z.number().min(1).max(100),
  cursor: z.string().max(100).optional()
});

// Validate all inputs
function validateInput(input: unknown, schema: z.ZodSchema) {
  try {
    return schema.parse(input);
  } catch (error) {
    throw new ValidationError('Invalid input', error);
  }
}
```

### Transport Security

```nginx
# HTTPS only with modern TLS
server {
  listen 443 ssl http2;
  
  # TLS 1.3 preferred, 1.2 minimum
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!aNULL:!MD5;
  ssl_prefer_server_ciphers on;
  
  # HSTS
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  
  # Additional security headers
  add_header X-Frame-Options "DENY" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-XSS-Protection "1; mode=block" always;
}
```

## Privacy Protection

### Data Minimization Principles

1. **No PII Collection**: Protocol explicitly excludes personal data
2. **Anonymized Analytics**: Only aggregate metrics, no individual tracking
3. **Ephemeral Sessions**: No persistent identifiers
4. **Local Processing**: Prefer client-side computation

### GDPR Compliance

```typescript
// Example: Review aggregation without PII
interface AnonymizedReview {
  product_id: string;
  rating: number;
  text?: string;  // Sanitized, no names/emails
  verified_purchase: boolean;
  // No: reviewer_name, email, user_id, ip_address
}

// Sanitize review text
function sanitizeReviewText(text: string): string {
  // Remove emails
  text = text.replace(/\S+@\S+\.\S+/g, '[email]');
  
  // Remove phone numbers
  text = text.replace(/[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}/g, '[phone]');
  
  // Remove potential names (basic heuristic)
  text = text.replace(/@\w+/g, '[mention]');
  
  return text;
}
```

## Audit Logging

### Security Event Logging

```typescript
interface SecurityEvent {
  timestamp: string;
  event_type: 'signature_verification' | 'rate_limit' | 'capsule_violation';
  client_id?: string;
  details: Record<string, any>;
  severity: 'info' | 'warning' | 'critical';
}

class SecurityLogger {
  log(event: SecurityEvent) {
    // Log to SIEM
    this.siem.send(event);
    
    // Critical events trigger alerts
    if (event.severity === 'critical') {
      this.alerting.trigger(event);
    }
  }
}
```

### Compliance Audit Trail

```typescript
// Track data access for compliance
class AuditTrail {
  async logDataAccess(request: DataAccessRequest) {
    await this.store.append({
      timestamp: new Date().toISOString(),
      request_id: request.id,
      tool: request.tool,
      client_id: request.client_id,
      ip_hash: this.hashIP(request.ip),  // Hash for privacy
      result: request.result,
      duration_ms: request.duration
    });
  }
}
```

## Security Checklist

### Implementation

- [ ] **Cryptography**
  - [ ] Ed25519 or RSA-2048 minimum for signatures
  - [ ] Secure key storage (HSM/KMS)
  - [ ] Regular key rotation schedule
  - [ ] Public key publication via DID/well-known

- [ ] **Capsule Security**
  - [ ] Strict CSP headers
  - [ ] Iframe sandboxing enabled
  - [ ] Resource limits enforced
  - [ ] Auto-termination on timeout
  - [ ] Origin validation on messages

- [ ] **Network Security**
  - [ ] HTTPS only (TLS 1.2+)
  - [ ] Rate limiting per client
  - [ ] Input validation on all endpoints
  - [ ] Query complexity limits
  - [ ] DDoS protection

- [ ] **Privacy**
  - [ ] No PII in any data structure
  - [ ] Review text sanitization
  - [ ] IP address hashing/removal
  - [ ] Cookie-free implementation
  - [ ] GDPR compliance verified

- [ ] **Monitoring**
  - [ ] Security event logging
  - [ ] Anomaly detection
  - [ ] Failed signature alerts
  - [ ] Rate limit violations tracked
  - [ ] Capsule violations logged

### Testing

```bash
# Security testing commands
npm run security:audit        # Dependency vulnerabilities
npm run security:pentest      # Penetration testing suite
npm run security:capsule      # Capsule escape attempts
npm run security:fuzzing      # Input fuzzing tests
```

## Incident Response

### Response Plan

1. **Detection**: Automated alerts on security events
2. **Triage**: Assess severity and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Update security measures

### Contact

Security issues should be reported to: security@agentic-commerce.org

Response time:
- Critical: 4 hours
- High: 24 hours  
- Medium: 72 hours
- Low: 7 days

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CSP Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [W3C DID Specification](https://www.w3.org/TR/did-core/)
- [GDPR Guidelines](https://gdpr.eu/)

---

*Last updated: 2025-09-18*
*Security Model Version: 0.1.0*
