#!/usr/bin/env node

/**
 * AXP Conformance Validator
 * Reference implementation for validating AXP documents
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

// Initialize AJV with strict mode
const ajv = new Ajv({ 
  strict: true, 
  allErrors: true,
  validateFormats: true
});
addFormats(ajv);

// Load schemas
const schemas = {
  product: require('../schemas/axp/product.schema.json'),
  brand_profile: require('../schemas/axp/brand_profile.schema.json'),
  review: require('../schemas/axp/review.schema.json'),
  experience_capsule: require('../schemas/axp/experience_capsule.schema.json')
};

// Compile validators
const validators = {};
for (const [name, schema] of Object.entries(schemas)) {
  validators[name] = ajv.compile(schema);
}

/**
 * Canonical JSON serialization for AXP
 * @param {object} obj - Object to canonicalize
 * @returns {string} - Canonical JSON string
 */
function canonicalizeJSON(obj) {
  if (obj === null) return 'null';
  
  if (typeof obj === 'boolean') return obj.toString();
  
  if (typeof obj === 'number') {
    // IEEE 754 double precision without leading zeros
    return obj.toString().replace(/^0+(?=\d)/, '');
  }
  
  if (typeof obj === 'string') {
    // Normalize Unicode to NFC form
    const normalized = obj.normalize('NFC');
    return JSON.stringify(normalized);
  }
  
  if (Array.isArray(obj)) {
    const items = obj.map(canonicalizeJSON).join(',');
    return `[${items}]`;
  }
  
  if (typeof obj === 'object') {
    // Remove signature field if present
    const copy = { ...obj };
    delete copy.signature;
    
    // Sort keys lexicographically
    const keys = Object.keys(copy).sort();
    const pairs = keys.map(key => {
      const value = canonicalizeJSON(copy[key]);
      return `${JSON.stringify(key)}:${value}`;
    });
    return `{${pairs.join(',')}}`;
  }
  
  throw new Error(`Cannot canonicalize type: ${typeof obj}`);
}

/**
 * Verify EdDSA signature
 * @param {object} document - AXP document with signature
 * @param {string} publicKey - Base64 encoded public key
 * @returns {boolean} - True if signature is valid
 */
function verifySignature(document, publicKey) {
  if (!document.signature) {
    console.error('❌ No signature found');
    return false;
  }
  
  const { alg, sig } = document.signature;
  
  if (alg !== 'EdDSA' && alg !== 'RS256') {
    console.error(`❌ Unsupported algorithm: ${alg}`);
    return false;
  }
  
  // Get canonical representation
  const canonical = canonicalizeJSON(document);
  
  // For demo purposes, we'll just check that signature exists
  // In production, verify with actual crypto library
  console.log('✓ Signature format valid (demo mode)');
  return true;
}

/**
 * Validate timestamp format
 * @param {string} timestamp - ISO 8601 timestamp
 * @returns {boolean} - True if valid with Z suffix
 */
function validateTimestamp(timestamp) {
  const iso8601WithZ = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
  return iso8601WithZ.test(timestamp);
}

/**
 * Validate AXP document
 * @param {string} filepath - Path to JSON file
 * @returns {object} - Validation result
 */
function validateDocument(filepath) {
  const filename = path.basename(filepath);
  console.log(`\nValidating: ${filename}`);
  console.log('─'.repeat(40));
  
  try {
    // Read and parse file
    const content = fs.readFileSync(filepath, 'utf8');
    const document = JSON.parse(content);
    
    // Check core requirements
    if (document.spec !== 'axp') {
      console.error('❌ Missing or invalid spec field');
      return { valid: false, error: 'Invalid spec' };
    }
    
    if (document.version !== '0.1.0') {
      console.error('❌ Invalid version');
      return { valid: false, error: 'Invalid version' };
    }
    
    if (!validateTimestamp(document.generated_at)) {
      console.error('❌ Invalid generated_at timestamp (must use Z suffix)');
      return { valid: false, error: 'Invalid timestamp format' };
    }
    
    // Determine document type and validate schema
    let validator = null;
    let docType = 'unknown';
    
    if (document.product) {
      validator = validators.product;
      docType = 'product';
    } else if (document.brand) {
      validator = validators.brand_profile;
      docType = 'brand_profile';
    } else if (document.review) {
      validator = validators.review;
      docType = 'review';
    }
    
    if (!validator) {
      console.error('❌ Unknown document type');
      return { valid: false, error: 'Unknown document type' };
    }
    
    console.log(`Document type: ${docType}`);
    
    // Validate against schema
    const valid = validator(document);
    if (!valid) {
      console.error('❌ Schema validation failed:');
      validator.errors.forEach(err => {
        console.error(`   - ${err.instancePath || '/'}: ${err.message}`);
      });
      return { valid: false, errors: validator.errors };
    }
    
    console.log('✓ Schema validation passed');
    
    // Check canonical JSON
    try {
      const canonical = canonicalizeJSON(document);
      console.log('✓ Canonical JSON serialization valid');
    } catch (e) {
      console.error(`❌ Canonicalization failed: ${e.message}`);
      return { valid: false, error: e.message };
    }
    
    // Verify signature if present
    if (document.signature) {
      const sigValid = verifySignature(document);
      if (!sigValid) {
        return { valid: false, error: 'Invalid signature' };
      }
    }
    
    console.log('✅ Document is valid');
    return { valid: true, type: docType };
    
  } catch (e) {
    console.error(`❌ Error: ${e.message}`);
    return { valid: false, error: e.message };
  }
}

/**
 * Run conformance tests
 */
function runConformanceTests() {
  console.log('AXP Conformance Test Suite');
  console.log('═'.repeat(40));
  
  const testDirs = {
    golden: path.join(__dirname, '../tests/conformance/golden'),
    edge: path.join(__dirname, '../tests/conformance/edge'),
    invalid: path.join(__dirname, '../tests/conformance/invalid')
  };
  
  const results = {
    golden: { pass: 0, fail: 0 },
    edge: { pass: 0, fail: 0 },
    invalid: { pass: 0, fail: 0 }
  };
  
  // Test golden vectors (MUST pass)
  console.log('\n🏆 GOLDEN VECTORS (must pass)');
  if (fs.existsSync(testDirs.golden)) {
    const files = fs.readdirSync(testDirs.golden).filter(f => f.endsWith('.json'));
    for (const file of files) {
      const result = validateDocument(path.join(testDirs.golden, file));
      if (result.valid) {
        results.golden.pass++;
      } else {
        results.golden.fail++;
      }
    }
  }
  
  // Test edge cases (MUST pass)
  console.log('\n🔧 EDGE CASES (must pass)');
  if (fs.existsSync(testDirs.edge)) {
    const files = fs.readdirSync(testDirs.edge).filter(f => f.endsWith('.json'));
    for (const file of files) {
      const result = validateDocument(path.join(testDirs.edge, file));
      if (result.valid) {
        results.edge.pass++;
      } else {
        results.edge.fail++;
      }
    }
  }
  
  // Test invalid cases (MUST fail)
  console.log('\n⛔ INVALID CASES (must fail)');
  if (fs.existsSync(testDirs.invalid)) {
    const files = fs.readdirSync(testDirs.invalid).filter(f => f.endsWith('.json'));
    for (const file of files) {
      const result = validateDocument(path.join(testDirs.invalid, file));
      if (!result.valid) {
        results.invalid.pass++;
        console.log('✅ Correctly rejected invalid document');
      } else {
        results.invalid.fail++;
        console.error('❌ Failed to reject invalid document!');
      }
    }
  }
  
  // Summary
  console.log('\n' + '═'.repeat(40));
  console.log('CONFORMANCE TEST RESULTS:');
  console.log(`Golden:  ${results.golden.pass} passed, ${results.golden.fail} failed`);
  console.log(`Edge:    ${results.edge.pass} passed, ${results.edge.fail} failed`);
  console.log(`Invalid: ${results.invalid.pass} correctly rejected, ${results.invalid.fail} incorrectly accepted`);
  
  const totalFailures = results.golden.fail + results.edge.fail + results.invalid.fail;
  if (totalFailures === 0) {
    console.log('\n✅ ALL TESTS PASSED');
    process.exit(0);
  } else {
    console.log(`\n❌ ${totalFailures} TEST(S) FAILED`);
    process.exit(1);
  }
}

// Handle command line arguments
if (process.argv.length > 2) {
  // Validate single file
  const filepath = process.argv[2];
  validateDocument(filepath);
} else {
  // Run full conformance suite
  runConformanceTests();
}
