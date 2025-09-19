/**
 * AXP Protocol MCP Server
 * Minimal implementation with in-memory store
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { createHash } from "crypto";
import { z } from "zod";
import { extendedTools, ExtendedHandlers } from "./extended-tools.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

// ============================================================================
// Data Store
// ============================================================================

class InMemoryStore {
  private brandProfile: any;
  private products: Map<string, any> = new Map();
  private reviews: any[] = [];
  private capsules: Map<string, any> = new Map();
  private inventorySubscriptions: Map<string, Set<string>> = new Map();

  constructor() {
    this.loadExampleData();
  }

  private loadExampleData() {
    try {
      // Load brand profile
      const brandPath = join(__dirname, "../../examples/data/brand_profile.json");
      if (existsSync(brandPath)) {
        this.brandProfile = JSON.parse(readFileSync(brandPath, "utf-8"));
      }

      // Load products
      const productsPath = join(__dirname, "../../examples/data/catalog_products.jsonl");
      if (existsSync(productsPath)) {
        const lines = readFileSync(productsPath, "utf-8").split("\n").filter(l => l.trim());
        for (const line of lines) {
          const wrapper = JSON.parse(line);
          if (wrapper.product) {
            this.products.set(wrapper.product.id, wrapper.product);
          }
        }
      }

      // Load reviews
      const reviewsPath = join(__dirname, "../../examples/data/ratings_reviews.jsonl");
      if (existsSync(reviewsPath)) {
        const lines = readFileSync(reviewsPath, "utf-8").split("\n").filter(l => l.trim());
        for (const line of lines) {
          this.reviews.push(JSON.parse(line));
        }
      }

      // Mock capsules
      this.capsules.set("cap_sneaker_3d", {
        id: "cap_sneaker_3d",
        name: "3D Sneaker Configurator",
        version: "0.1.0",
        entry: { html: "index.html" },
        surfaces: ["canvas3d", "html"],
        sandbox_policy: {
          dom: true,
          storage: "none",
          network: {
            allow: ["https://cdn.urban-footwear.com/assets/"],
            block_all_others: true
          },
          lifetime_seconds: 600,
          permissions: []
        },
        api: {
          inbound_events: ["init", "configure", "set_variant", "request_quote"],
          outbound_events: ["ready", "state_changed", "add_to_cart", "telemetry"]
        }
      });

      this.capsules.set("cap_gait_analysis", {
        id: "cap_gait_analysis",
        name: "AI Gait Analyzer",
        version: "0.1.0",
        entry: { html: "gait.html" },
        surfaces: ["html"],
        sandbox_policy: {
          dom: true,
          storage: "memory",
          network: {
            allow: ["https://cdn.urban-footwear.com/api/gait/"],
            block_all_others: true
          },
          lifetime_seconds: 900,
          permissions: ["camera"]
        },
        api: {
          inbound_events: ["init", "analyze", "reset"],
          outbound_events: ["ready", "analysis_complete", "recommendation"]
        }
      });

    } catch (error) {
      console.error("Error loading example data:", error);
    }
  }

  getBrandProfile() {
    return this.brandProfile;
  }
  
  getProduct(productId: string): any {
    return this.products.get(productId);
  }
  
  getCapsule(capsuleId: string): any {
    return this.capsules.get(capsuleId);
  }

  searchProducts(query?: string, filters?: any, limit = 20, cursor?: string) {
    let results = Array.from(this.products.values());

    // Simple text search
    if (query) {
      const searchTerms = query.toLowerCase().split(" ");
      results = results.filter(product => {
        const searchText = `${product.title} ${product.short_desc || ""}`.toLowerCase();
        return searchTerms.some(term => searchText.includes(term));
      });
    }

    // Apply filters
    if (filters) {
      // Price filter
      if (filters.price) {
        if (filters.price.min !== undefined) {
          results = results.filter(p => p.price.value >= filters.price.min);
        }
        if (filters.price.max !== undefined) {
          results = results.filter(p => p.price.value <= filters.price.max);
        }
      }

      // Availability filter
      if (filters.availability && filters.availability.length > 0) {
        results = results.filter(p => filters.availability.includes(p.availability.state));
      }

      // Intent filter
      if (filters.intent && filters.intent.length > 0) {
        results = results.filter(p => {
          if (!p.intent_signals) return false;
          return p.intent_signals.some((signal: any) => 
            filters.intent.includes(signal.intent)
          );
        });
      }

      // Soft signal minimum filters
      if (filters.soft_min) {
        for (const [key, minValue] of Object.entries(filters.soft_min)) {
          if (minValue !== undefined && minValue !== null) {
            results = results.filter(p => {
              if (!p.soft_signals) return false;
              const score = p.soft_signals[key];
              return score !== undefined && score >= minValue;
            });
          }
        }
      }
    }

    // Apply cursor-based pagination (simple implementation)
    let startIndex = 0;
    if (cursor) {
      const cursorIndex = parseInt(cursor, 10);
      if (!isNaN(cursorIndex)) {
        startIndex = cursorIndex;
      }
    }

    const paginatedResults = results.slice(startIndex, startIndex + limit);
    const nextCursor = startIndex + limit < results.length 
      ? (startIndex + limit).toString() 
      : undefined;

    return {
      items: paginatedResults,
      next_cursor: nextCursor
    };
  }

  getProduct(productId: string) {
    return this.products.get(productId);
  }

  getCapsule(capsuleId: string) {
    return this.capsules.get(capsuleId);
  }

  createInventorySubscription(productIds: string[]): string {
    const subscriptionId = `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.inventorySubscriptions.set(subscriptionId, new Set(productIds));
    return subscriptionId;
  }
}

// ============================================================================
// Input Validation Schemas
// ============================================================================

const SearchCatalogSchema = z.object({
  query: z.string().optional(),
  filters: z.object({
    price: z.object({
      min: z.number().min(0).optional(),
      max: z.number().min(0).optional()
    }).optional(),
    availability: z.array(z.enum(["in_stock", "out_of_stock", "preorder", "discontinued"])).optional(),
    intent: z.array(z.string()).optional(),
    soft_min: z.object({
      uniqueness_score: z.number().min(0).max(1).optional(),
      craftsmanship_score: z.number().min(0).max(1).optional(),
      sustainability_score: z.number().min(0).max(1).optional(),
      innovation_score: z.number().min(0).max(1).optional()
    }).optional()
  }).optional(),
  limit: z.number().min(1).max(100).default(20),
  cursor: z.string().optional()
});

const GetProductSchema = z.object({
  product_id: z.string()
});

const GetExportSchema = z.object({
  since: z.string().optional()
});

const GetCapsuleSchema = z.object({
  capsule_id: z.string()
});

const SubscribeInventorySchema = z.object({
  product_ids: z.array(z.string()).min(1).max(100)
});

// ============================================================================
// MCP Server Implementation
// ============================================================================

class AXPServer {
  private server: Server;
  private store: InMemoryStore;
  private extendedHandlers: ExtendedHandlers;

  constructor() {
    this.store = new InMemoryStore();
    this.extendedHandlers = new ExtendedHandlers(this.store);
    this.server = new Server(
      {
        name: "axp-protocol-server",
        version: "0.1.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: this.getToolDefinitions(),
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "axp.getBrandProfile":
            return this.handleGetBrandProfile();

          case "axp.searchCatalog":
            return this.handleSearchCatalog(args);

          case "axp.getProduct":
            return this.handleGetProduct(args);

          case "axp.getExport":
            return this.handleGetExport(args);

          case "axp.getCapsule":
            return this.handleGetCapsule(args);

          case "axp.subscribeInventory":
            return this.handleSubscribeInventory(args);

          case "axp.health":
            return this.handleHealth();
            
          case "axp.listExperiences":
            return this.extendedHandlers.handleListExperiences(args);
            
          case "axp.getVariantMatrix":
            return this.extendedHandlers.handleGetVariantMatrix(args);
            
          case "axp.resolveVariant":
            return this.extendedHandlers.handleResolveVariant(args);
            
          case "axp.getProductRelations":
            return this.extendedHandlers.handleGetProductRelations(args);
            
          case "axp.getSignals":
            return this.extendedHandlers.handleGetSignals(args);
            
          case "axp.requestExperienceSession":
            return this.extendedHandlers.handleRequestExperienceSession(args);

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error: any) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                error: {
                  code: "AXP_ERROR",
                  message: error.message || "An error occurred",
                  details: error.details || {}
                }
              }, null, 2)
            }
          ],
        };
      }
    });
  }

  private getToolDefinitions(): Tool[] {
    return [
      {
        name: "axp.getBrandProfile",
        description: "Retrieve complete brand profile with trust signals",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "axp.searchCatalog",
        description: "Search products with rich filtering on soft signals",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query" },
            filters: {
              type: "object",
              properties: {
                price: {
                  type: "object",
                  properties: {
                    min: { type: "number" },
                    max: { type: "number" }
                  }
                },
                availability: {
                  type: "array",
                  items: { type: "string" }
                },
                intent: {
                  type: "array",
                  items: { type: "string" }
                },
                soft_min: {
                  type: "object",
                  properties: {
                    uniqueness_score: { type: "number" },
                    craftsmanship_score: { type: "number" },
                    sustainability_score: { type: "number" },
                    innovation_score: { type: "number" }
                  }
                }
              }
            },
            limit: { type: "number", default: 20 },
            cursor: { type: "string" }
          }
        }
      },
      {
        name: "axp.getProduct",
        description: "Get complete product details including experiences and trust data",
        inputSchema: {
          type: "object",
          required: ["product_id"],
          properties: {
            product_id: { type: "string" }
          }
        }
      },
      {
        name: "axp.getExport",
        description: "Download complete catalog as signed bundle",
        inputSchema: {
          type: "object",
          properties: {
            since: { type: "string", description: "ISO 8601 timestamp" }
          }
        }
      },
      {
        name: "axp.getCapsule",
        description: "Retrieve sandboxed experience capsule configuration",
        inputSchema: {
          type: "object",
          required: ["capsule_id"],
          properties: {
            capsule_id: { type: "string" }
          }
        }
      },
      {
        name: "axp.subscribeInventory",
        description: "Subscribe to real-time inventory updates",
        inputSchema: {
          type: "object",
          required: ["product_ids"],
          properties: {
            product_ids: {
              type: "array",
              items: { type: "string" },
              minItems: 1,
              maxItems: 100
            }
          }
        }
      },
      {
        name: "axp.health",
        description: "Check server health status",
        inputSchema: {
          type: "object",
          properties: {}
        }
      },
      ...extendedTools
    ];
  }

  private handleGetBrandProfile() {
    const profile = this.store.getBrandProfile();
    if (!profile) {
      throw new Error("Brand profile not found");
    }
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(profile, null, 2)
        }
      ],
    };
  }

  private handleSearchCatalog(args: any) {
    const validated = SearchCatalogSchema.parse(args || {});
    const results = this.store.searchProducts(
      validated.query,
      validated.filters,
      validated.limit,
      validated.cursor
    );
    
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(results, null, 2)
        }
      ],
    };
  }

  private handleGetProduct(args: any) {
    const { product_id } = GetProductSchema.parse(args);
    const product = this.store.getProduct(product_id);
    
    if (!product) {
      throw new Error(`Product not found: ${product_id}`);
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ product }, null, 2)
        }
      ],
    };
  }

  private handleGetExport(args: any) {
    const validated = GetExportSchema.parse(args || {});
    
    // Generate mock export bundle info
    const bundleData = JSON.stringify({
      manifest: this.store.getBrandProfile(),
      timestamp: new Date().toISOString()
    });
    
    const hash = createHash("sha256").update(bundleData).digest("hex");
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            bundle_uri: `axp://export/axp_bundle_${new Date().toISOString().split("T")[0]}.zip`,
            checksum_sha256: hash,
            expires_at: expiresAt.toISOString()
          }, null, 2)
        }
      ],
    };
  }

  private handleGetCapsule(args: any) {
    const { capsule_id } = GetCapsuleSchema.parse(args);
    const capsule = this.store.getCapsule(capsule_id);
    
    if (!capsule) {
      throw new Error(`Capsule not found: ${capsule_id}`);
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            capsule_uri: `axp://capsules/${capsule_id}.zip`,
            sandbox_embed: {
              kind: "iframe",
              policy: {
                allow_scripts: true,
                allow_forms: false,
                allow_fullscreen: false
              },
              preferred_size: {
                width: 720,
                height: 480
              }
            }
          }, null, 2)
        }
      ],
    };
  }

  private handleSubscribeInventory(args: any) {
    const { product_ids } = SubscribeInventorySchema.parse(args);
    const subscriptionId = this.store.createInventorySubscription(product_ids);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            subscription_id: subscriptionId,
            ttl_seconds: 600
          }, null, 2)
        }
      ],
    };
  }

  private handleHealth() {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            status: "ok",
            version: "0.1.0",
            uptime: process.uptime(),
            timestamp: new Date().toISOString()
          }, null, 2)
        }
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("AXP MCP Server running on stdio");
  }
}

// ============================================================================
// Main Entry Point
// ============================================================================

if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new AXPServer();
  server.run().catch((error) => {
    console.error("Server error:", error);
    process.exit(1);
  });
}
