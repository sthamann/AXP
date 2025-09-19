/**
 * Extended MCP Tools for AXP Protocol
 * 
 * Provides comprehensive toolset for AI agents to interact with AXP data
 * including filtered searches, enrichment status, and granular field selection.
 */

import { Tool, ToolResult } from '@modelcontextprotocol/sdk';

// Tool definitions for extended MCP functionality
export const extendedTools: Tool[] = [
  {
    name: 'axp.getBrandProfile',
    description: 'Get complete brand profile with all extensions',
    inputSchema: {
      type: 'object',
      properties: {
        brand_id: {
          type: 'string',
          description: 'Brand identifier'
        },
        include_fields: {
          type: 'array',
          items: { type: 'string' },
          description: 'Specific fields to include (default: all)'
        },
        include_enrichment: {
          type: 'boolean',
          description: 'Include third-party enrichment data',
          default: false
        }
      },
      required: ['brand_id']
    }
  },
  
  {
    name: 'axp.getProduct',
    description: 'Get product with field selection and enrichment',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Product identifier (SKU)'
        },
        fields: {
          type: 'array',
          items: {
            type: 'string',
            enum: [
              'basic',           // id, title, price, availability
              'identifiers',     // GTIN, MPN, ISBN
              'taxonomy',        // Google category, HS code
              'pricing',         // Full pricing with tiers
              'shipping',        // Weight, dimensions, lead time
              'regulatory',      // Compliance info
              'warranty',        // Warranty details
              'b2b',            // B2B pricing and terms
              'digital',        // Digital product info
              'trust_signals',  // Reviews, returns
              'intent_signals', // Intent with confidence
              'compatibility',  // Related products
              'experiences'     // Capsules
            ]
          },
          description: 'Field groups to include',
          default: ['basic', 'trust_signals']
        },
        with_variants: {
          type: 'boolean',
          description: 'Include all variants',
          default: false
        }
      },
      required: ['product_id']
    }
  },
  
  {
    name: 'axp.searchCatalog',
    description: 'Advanced catalog search with rich filtering',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query'
        },
        filters: {
          type: 'object',
          properties: {
            intent: {
              type: 'array',
              items: { type: 'string' },
              description: 'Filter by intent signals'
            },
            trust_min: {
              type: 'number',
              minimum: 0,
              maximum: 1,
              description: 'Minimum trust score'
            },
            price_range: {
              type: 'object',
              properties: {
                min: { type: 'number' },
                max: { type: 'number' },
                currency: { type: 'string' }
              }
            },
            ships_to: {
              type: 'string',
              pattern: '^[A-Z]{2}$',
              description: 'ISO country code for shipping'
            },
            in_stock: {
              type: 'boolean',
              description: 'Only in-stock items'
            },
            has_reviews: {
              type: 'boolean',
              description: 'Only items with reviews'
            },
            min_rating: {
              type: 'number',
              minimum: 1,
              maximum: 5,
              description: 'Minimum average rating'
            },
            max_return_rate: {
              type: 'number',
              minimum: 0,
              maximum: 1,
              description: 'Maximum acceptable return rate'
            },
            categories: {
              type: 'array',
              items: { type: 'string' },
              description: 'Google product categories'
            },
            regulatory: {
              type: 'object',
              properties: {
                ce_marking: { type: 'boolean' },
                age_rating_max: { type: 'string' },
                no_hazmat: { type: 'boolean' }
              }
            }
          }
        },
        sort: {
          type: 'object',
          properties: {
            field: {
              type: 'string',
              enum: ['relevance', 'price', 'rating', 'return_rate', 'trust_score']
            },
            order: {
              type: 'string',
              enum: ['asc', 'desc']
            }
          }
        },
        pagination: {
          type: 'object',
          properties: {
            limit: {
              type: 'integer',
              minimum: 1,
              maximum: 100,
              default: 20
            },
            offset: {
              type: 'integer',
              minimum: 0,
              default: 0
            }
          }
        },
        explain: {
          type: 'boolean',
          description: 'Include scoring explanation',
          default: false
        }
      }
    }
  },
  
  {
    name: 'axp.listCapsules',
    description: 'List available experience capsules',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Filter by product'
        },
        modality: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['canvas3d', 'ar', 'vr', 'configurator', 'comparison']
          },
          description: 'Filter by experience type'
        }
      }
    }
  },
  
  {
    name: 'axp.getCapsuleManifest',
    description: 'Get experience capsule manifest with security policy',
    inputSchema: {
      type: 'object',
      properties: {
        capsule_id: {
          type: 'string',
          description: 'Capsule identifier'
        },
        validate_signature: {
          type: 'boolean',
          description: 'Verify capsule signature',
          default: true
        }
      },
      required: ['capsule_id']
    }
  },
  
  {
    name: 'axp.getReviews',
    description: 'Get product reviews with provider filtering',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Product identifier'
        },
        providers: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['trustpilot', 'trusted_shops', 'google', 'internal']
          },
          description: 'Review sources to include'
        },
        verified_only: {
          type: 'boolean',
          description: 'Only verified purchases',
          default: false
        },
        min_rating: {
          type: 'integer',
          minimum: 1,
          maximum: 5
        },
        language: {
          type: 'string',
          pattern: '^[a-z]{2}$',
          description: 'ISO 639-1 language code'
        },
        date_from: {
          type: 'string',
          format: 'date',
          description: 'Reviews from this date'
        },
        limit: {
          type: 'integer',
          minimum: 1,
          maximum: 100,
          default: 10
        }
      }
    }
  },
  
  {
    name: 'axp.getEnrichmentStatus',
    description: 'Check third-party data freshness and availability',
    inputSchema: {
      type: 'object',
      properties: {
        entity_type: {
          type: 'string',
          enum: ['brand', 'product'],
          description: 'Entity type to check'
        },
        entity_id: {
          type: 'string',
          description: 'Entity identifier'
        },
        providers: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['trustpilot', 'trusted_shops', 'builtwith', 'google_seller']
          },
          description: 'Providers to check'
        }
      },
      required: ['entity_type', 'entity_id']
    }
  },
  
  {
    name: 'axp.calculateIntent',
    description: 'Calculate intent signals for a product',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Product to analyze'
        },
        window_days: {
          type: 'integer',
          minimum: 1,
          maximum: 365,
          default: 90,
          description: 'Analysis window'
        },
        methods: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['events', 'text', 'purchase_patterns', 'returns']
          },
          description: 'Analysis methods to use'
        },
        min_confidence: {
          type: 'number',
          minimum: 0,
          maximum: 1,
          default: 0.7,
          description: 'Minimum confidence threshold'
        }
      },
      required: ['product_id']
    }
  },
  
  {
    name: 'axp.getKPIs',
    description: 'Get calculated KPIs with methodology',
    inputSchema: {
      type: 'object',
      properties: {
        entity_type: {
          type: 'string',
          enum: ['brand', 'product', 'category']
        },
        entity_id: {
          type: 'string'
        },
        kpis: {
          type: 'array',
          items: {
            type: 'string',
            enum: [
              'return_rate',
              'dispute_rate',
              'chargeback_rate',
              'on_time_rate',
              'csat',
              'nps',
              'fit_hint_score',
              'reliability_score',
              'performance_score',
              'owner_satisfaction'
            ]
          },
          description: 'KPIs to retrieve'
        },
        include_formula: {
          type: 'boolean',
          description: 'Include calculation formula',
          default: false
        },
        include_confidence: {
          type: 'boolean',
          description: 'Include confidence intervals',
          default: true
        }
      },
      required: ['entity_type', 'entity_id']
    }
  },
  
  {
    name: 'axp.compareProducts',
    description: 'Compare multiple products side-by-side',
    inputSchema: {
      type: 'object',
      properties: {
        product_ids: {
          type: 'array',
          items: { type: 'string' },
          minItems: 2,
          maxItems: 5,
          description: 'Products to compare'
        },
        aspects: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['price', 'features', 'trust', 'intent', 'availability', 'shipping']
          },
          description: 'Aspects to compare',
          default: ['price', 'trust', 'features']
        },
        normalize_scores: {
          type: 'boolean',
          description: 'Normalize scores for comparison',
          default: true
        }
      },
      required: ['product_ids']
    }
  },
  
  {
    name: 'axp.getVariantMatrix',
    description: 'Get complete variant matrix for a product',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Parent product ID'
        },
        in_stock_only: {
          type: 'boolean',
          description: 'Filter to available variants',
          default: false
        },
        ship_to: {
          type: 'string',
          pattern: '^[A-Z]{2}$',
          description: 'Filter by shipping destination'
        }
      },
      required: ['product_id']
    }
  },
  
  {
    name: 'axp.resolveVariant',
    description: 'Find specific variant by options',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Parent product ID'
        },
        options: {
          type: 'object',
          additionalProperties: { type: 'string' },
          description: 'Variant options (e.g., {color: "red", size: "42"})'
        }
      },
      required: ['product_id', 'options']
    }
  },
  
  {
    name: 'axp.getRelatedProducts',
    description: 'Get related products and accessories',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Reference product'
        },
        relationship_types: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['accessories', 'alternatives', 'frequently_bought', 'spare_parts', 'upgrades']
          },
          description: 'Types of relationships to include'
        },
        limit: {
          type: 'integer',
          minimum: 1,
          maximum: 20,
          default: 5
        }
      },
      required: ['product_id']
    }
  },
  
  {
    name: 'axp.validateCompliance',
    description: 'Check product compliance for target market',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Product to validate'
        },
        target_market: {
          type: 'string',
          pattern: '^[A-Z]{2}$',
          description: 'Target country code'
        },
        requirements: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['ce_marking', 'rohs', 'reach', 'weee', 'age_rating', 'food_safety']
          },
          description: 'Compliance requirements to check'
        }
      },
      required: ['product_id', 'target_market']
    }
  },
  
  {
    name: 'axp.getB2BTerms',
    description: 'Get B2B pricing and terms',
    inputSchema: {
      type: 'object',
      properties: {
        product_id: {
          type: 'string',
          description: 'Product identifier'
        },
        quantity: {
          type: 'integer',
          minimum: 1,
          description: 'Order quantity for pricing'
        },
        company_type: {
          type: 'string',
          enum: ['small_business', 'enterprise', 'government', 'education'],
          description: 'Buyer category'
        },
        payment_terms: {
          type: 'string',
          enum: ['prepaid', 'net_30', 'net_60', 'net_90'],
          description: 'Preferred payment terms'
        }
      },
      required: ['product_id']
    }
  }
];

// Type definitions for tool responses
export interface BrandProfileResponse {
  brand: {
    id: string;
    legal_name: string;
    domains: string[];
    founded_year: number;
    headquarters_country: string;
    // Extended fields based on requested includes
    legal?: any;
    payments?: any;
    fulfillment?: any;
    compliance?: any;
    policies?: any;
    tech_stack?: any;
    enrichment?: {
      trustpilot?: any;
      trusted_shops?: any;
      builtwith?: any;
    };
  };
  signature: string;
  last_verified: string;
  ttl_seconds: number;
}

export interface SearchResponse {
  items: Array<{
    product: any;
    relevance_score?: number;
    explanation?: string;
  }>;
  total_count: number;
  facets?: {
    categories: Record<string, number>;
    price_ranges: Array<{ min: number; max: number; count: number }>;
    intents: Record<string, number>;
  };
  next_offset?: number;
}

export interface EnrichmentStatusResponse {
  entity_type: string;
  entity_id: string;
  providers: Array<{
    name: string;
    status: 'fresh' | 'stale' | 'missing' | 'error';
    last_updated?: string;
    ttl_remaining_seconds?: number;
    data_available: boolean;
    anomaly_detected?: boolean;
  }>;
  recommended_refresh: string[];
}

export interface KPIResponse {
  entity_type: string;
  entity_id: string;
  kpis: Array<{
    name: string;
    value: number;
    window_days: number;
    sample_size: number;
    confidence?: number;
    confidence_interval?: [number, number];
    method: string;
    formula?: string;
    calculated_at: string;
    ttl_seconds: number;
  }>;
}

// Implementation would connect to actual data sources
// This is the interface definition for the MCP protocol
