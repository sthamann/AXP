#!/usr/bin/env node

/**
 * AXP Bundle Creator
 * Generates a signed AXP export bundle from example data
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const archiver = require('archiver');

class BundleCreator {
  constructor() {
    this.dataDir = path.join(__dirname, '..', 'examples', 'data');
    this.capsulesDir = path.join(__dirname, '..', 'examples', 'capsules');
    this.outputDir = path.join(__dirname, '..', 'exports');
  }

  async create() {
    console.log('🔨 Creating AXP Bundle...\n');

    // Ensure output directory exists
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().split('T')[0];
    const bundlePath = path.join(this.outputDir, `axp_bundle_${timestamp}.zip`);

    // Create zip archive
    const output = fs.createWriteStream(bundlePath);
    const archive = archiver('zip', {
      zlib: { level: 9 } // Maximum compression
    });

    // Handle stream events
    output.on('close', () => {
      const size = (archive.pointer() / 1024).toFixed(2);
      console.log(`✅ Bundle created: ${bundlePath}`);
      console.log(`📦 Size: ${size} KB`);
      console.log(`📊 Total files: ${archive.pointer()} bytes`);
      
      // Generate checksum
      const checksum = this.generateChecksum(bundlePath);
      console.log(`🔐 SHA-256: ${checksum}`);
      
      // Create manifest file
      this.createManifestFile(bundlePath, checksum);
    });

    archive.on('warning', (err) => {
      if (err.code === 'ENOENT') {
        console.warn('⚠️  Warning:', err);
      } else {
        throw err;
      }
    });

    archive.on('error', (err) => {
      throw err;
    });

    // Pipe archive data to the file
    archive.pipe(output);

    // Add manifest
    const manifest = this.createManifest();
    archive.append(JSON.stringify(manifest, null, 2), { name: 'manifest.json' });
    console.log('📄 Added manifest.json');

    // Add brand profile
    const brandProfilePath = path.join(this.dataDir, 'brand_profile.json');
    if (fs.existsSync(brandProfilePath)) {
      archive.file(brandProfilePath, { name: 'brand_profile.json' });
      console.log('🏢 Added brand_profile.json');
    }

    // Add catalog products
    const catalogPath = path.join(this.dataDir, 'catalog_products.jsonl');
    if (fs.existsSync(catalogPath)) {
      archive.file(catalogPath, { name: 'catalog_products.jsonl' });
      console.log('📦 Added catalog_products.jsonl');
    }

    // Add reviews
    const reviewsPath = path.join(this.dataDir, 'ratings_reviews.jsonl');
    if (fs.existsSync(reviewsPath)) {
      archive.file(reviewsPath, { name: 'ratings_reviews.jsonl' });
      console.log('⭐ Added ratings_reviews.jsonl');
    }

    // Add experiences (mock)
    const experiences = this.createExperiencesList();
    archive.append(experiences, { name: 'experiences.jsonl' });
    console.log('🎮 Added experiences.jsonl');

    // Add policies (mock)
    const policies = this.createPolicies();
    archive.append(JSON.stringify(policies, null, 2), { name: 'policies.json' });
    console.log('📋 Added policies.json');

    // Add capsules directory
    if (fs.existsSync(this.capsulesDir)) {
      archive.directory(this.capsulesDir, 'assets/capsules');
      console.log('🎯 Added capsules directory');
    }

    // Finalize the archive
    await archive.finalize();
  }

  createManifest() {
    const now = new Date().toISOString();
    
    const manifestData = {
      spec: 'axp',
      version: '0.1.0',
      publisher: {
        name: 'Urban Footwear Demo Store',
        domain: 'demo.urban-footwear.com',
        public_keys: ['did:web:demo.urban-footwear.com#axp-2025']
      },
      brand_profile: 'brand_profile.json',
      files: {
        catalog_products: 'catalog_products.jsonl',
        experiences: 'experiences.jsonl',
        policies: 'policies.json',
        ratings_reviews: 'ratings_reviews.jsonl'
      },
      generated_at: now,
      metadata: {
        product_count: 3,
        review_count: 8,
        capsule_count: 2,
        languages: ['en', 'de']
      }
    };

    // Generate signature (mock - in production use real crypto)
    const signature = this.generateSignature(manifestData);
    manifestData.signature = {
      alg: 'RS256',
      kid: 'did:web:demo.urban-footwear.com#axp-2025',
      value: signature
    };

    return manifestData;
  }

  createExperiencesList() {
    const experiences = [
      {
        id: 'exp_001',
        product_id: 'sku_123',
        capsule_id: 'cap_sneaker_3d',
        type: 'configurator',
        name: '3D Sneaker Configurator',
        description: 'Customize your sneaker in real-time 3D'
      },
      {
        id: 'exp_002',
        product_id: 'sku_456',
        capsule_id: 'cap_gait_analysis',
        type: 'analyzer',
        name: 'AI Gait Analyzer',
        description: 'Find your perfect running shoe with AI analysis'
      },
      {
        id: 'exp_003',
        product_id: 'sku_789',
        capsule_id: 'cap_impact_viz',
        type: 'visualizer',
        name: 'Ocean Impact Visualizer',
        description: 'See your environmental impact in real-time'
      }
    ];

    return experiences.map(exp => JSON.stringify(exp)).join('\n');
  }

  createPolicies() {
    return {
      spec: 'axp',
      version: '0.1.0',
      generated_at: new Date().toISOString(),
      policies: {
        shipping: {
          standard: {
            regions: ['DE', 'AT', 'CH', 'NL', 'BE', 'FR', 'IT', 'ES', 'PL'],
            days: 2,
            cost: {
              currency: 'EUR',
              value: 4.99,
              free_above: 50
            }
          },
          express: {
            regions: ['DE', 'AT', 'CH', 'NL'],
            days: 1,
            cost: {
              currency: 'EUR',
              value: 12.99
            }
          }
        },
        returns: {
          window_days: 30,
          restocking_fee: 0.0,
          conditions: [
            'unworn',
            'original_packaging',
            'tags_attached'
          ],
          process: {
            inspection_days: 2,
            refund_days: 5
          }
        },
        warranty: {
          standard_days: 365,
          extended_available: true,
          extended_days: 730,
          coverage: [
            'manufacturing_defects',
            'material_failure',
            'sole_separation'
          ]
        },
        privacy: {
          gdpr_compliant: true,
          data_retention_days: 90,
          cookies: 'essential_only',
          tracking: 'opt_in'
        }
      }
    };
  }

  generateSignature(data) {
    // Mock signature - in production, use real private key
    const message = JSON.stringify(data, Object.keys(data).sort());
    const hash = crypto.createHash('sha256').update(message).digest('base64url');
    
    // Simulate RSA signature structure
    return `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.${hash}.mock_signature_${Date.now()}`;
  }

  generateChecksum(filePath) {
    const fileBuffer = fs.readFileSync(filePath);
    const hashSum = crypto.createHash('sha256');
    hashSum.update(fileBuffer);
    return hashSum.digest('hex');
  }

  createManifestFile(bundlePath, checksum) {
    const manifestPath = bundlePath.replace('.zip', '_manifest.json');
    const manifest = {
      bundle: path.basename(bundlePath),
      checksum_sha256: checksum,
      created_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days
      download_uri: `axp://export/${path.basename(bundlePath)}`,
      size_bytes: fs.statSync(bundlePath).size
    };
    
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
    console.log(`\n📄 Manifest file created: ${manifestPath}`);
  }
}

// Check if archiver is installed
try {
  require.resolve('archiver');
} catch {
  console.log('📦 Installing required dependency: archiver');
  require('child_process').execSync('npm install archiver', { stdio: 'inherit' });
}

// Run the bundle creator
const creator = new BundleCreator();
creator.create().catch(error => {
  console.error('❌ Error creating bundle:', error);
  process.exit(1);
});
