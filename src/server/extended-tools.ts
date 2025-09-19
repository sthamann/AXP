/**
 * Extended AXP Protocol MCP Tools
 * New tools for variant management, experiences, and signals
 */

import { Tool } from "@modelcontextprotocol/sdk/types.js";

export const extendedTools: Tool[] = [
  {
    name: "axp.listExperiences",
    description: "List available experience capsules for a product",
    inputSchema: {
      type: "object",
      required: ["product_id"],
      properties: {
        product_id: { 
          type: "string",
          description: "Product ID to get experiences for"
        }
      }
    }
  },
  {
    name: "axp.getVariantMatrix",
    description: "Get variant axes and matrix for product options to SKU mapping",
    inputSchema: {
      type: "object",
      required: ["product_id"],
      properties: {
        product_id: { 
          type: "string",
          description: "Parent product ID"
        }
      }
    }
  },
  {
    name: "axp.resolveVariant",
    description: "Resolve specific variant SKU from product options",
    inputSchema: {
      type: "object",
      required: ["product_id", "options"],
      properties: {
        product_id: { 
          type: "string",
          description: "Parent product ID"
        },
        options: {
          type: "object",
          description: "Selected options (e.g., {color: 'black', size: '42'})",
          additionalProperties: { type: "string" }
        }
      }
    }
  },
  {
    name: "axp.getProductRelations",
    description: "Get product relationships (accessories, alternatives, replacements)",
    inputSchema: {
      type: "object",
      required: ["product_id"],
      properties: {
        product_id: { 
          type: "string",
          description: "Product ID"
        }
      }
    }
  },
  {
    name: "axp.getSignals",
    description: "Get all soft signals, trust signals, and content quality for a product",
    inputSchema: {
      type: "object",
      required: ["product_id"],
      properties: {
        product_id: { 
          type: "string",
          description: "Product ID"
        }
      }
    }
  },
  {
    name: "axp.requestExperienceSession",
    description: "Request a sandboxed session for an experience capsule",
    inputSchema: {
      type: "object",
      required: ["capsule_id", "product_id"],
      properties: {
        capsule_id: { 
          type: "string",
          description: "Experience capsule ID"
        },
        product_id: { 
          type: "string",
          description: "Product ID for context"
        },
        params: {
          type: "object",
          description: "Initial parameters for the experience",
          additionalProperties: true
        }
      }
    }
  }
];

export class ExtendedHandlers {
  constructor(private store: any) {}

  handleListExperiences(args: any) {
    const product = this.store.getProduct(args.product_id);
    if (!product) {
      throw new Error(`Product not found: ${args.product_id}`);
    }

    const experiences = product.experiences?.capsules || [];
    
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            product_id: args.product_id,
            experiences: experiences
          }, null, 2)
        }
      ]
    };
  }

  handleGetVariantMatrix(args: any) {
    const product = this.store.getProduct(args.product_id);
    if (!product) {
      throw new Error(`Product not found: ${args.product_id}`);
    }

    const axes = product.variant_axes || [];
    const variants = product.variants || [];
    
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            product_id: args.product_id,
            axes: axes,
            variants: variants.map((v: any) => ({
              sku: v.sku,
              options: v.options,
              price: v.price,
              availability: v.availability
            }))
          }, null, 2)
        }
      ]
    };
  }

  handleResolveVariant(args: any) {
    const product = this.store.getProduct(args.product_id);
    if (!product) {
      throw new Error(`Product not found: ${args.product_id}`);
    }

    const variants = product.variants || [];
    
    // Find matching variant
    const variant = variants.find((v: any) => {
      return Object.keys(args.options).every(key => 
        v.options[key] === args.options[key]
      );
    });

    if (!variant) {
      throw new Error(`No variant found for options: ${JSON.stringify(args.options)}`);
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            sku: variant.sku,
            price: variant.price,
            availability: variant.availability,
            media: variant.media_override || product.media,
            shipping: variant.shipping
          }, null, 2)
        }
      ]
    };
  }

  handleGetProductRelations(args: any) {
    const product = this.store.getProduct(args.product_id);
    if (!product) {
      throw new Error(`Product not found: ${args.product_id}`);
    }

    const relations = product.relations || {
      compatible_with: [],
      recommended_accessories: [],
      alternative_to: [],
      replacement_for: []
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            product_id: args.product_id,
            relations: relations
          }, null, 2)
        }
      ]
    };
  }

  handleGetSignals(args: any) {
    const product = this.store.getProduct(args.product_id);
    if (!product) {
      throw new Error(`Product not found: ${args.product_id}`);
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            product_id: args.product_id,
            soft_signals: product.soft_signals || {},
            trust_signals: product.trust_signals || {},
            content_quality: product.content_quality || {},
            agent_ranking_hint: product.agent_ranking_hint || {}
          }, null, 2)
        }
      ]
    };
  }

  handleRequestExperienceSession(args: any) {
    const capsule = this.store.getCapsule(args.capsule_id);
    if (!capsule) {
      throw new Error(`Capsule not found: ${args.capsule_id}`);
    }

    const product = this.store.getProduct(args.product_id);
    if (!product) {
      throw new Error(`Product not found: ${args.product_id}`);
    }

    // Generate session token
    const sessionToken = `ses_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const expiresAt = new Date(Date.now() + 600000).toISOString(); // 10 minutes

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            session_token: sessionToken,
            sandbox_embed: {
              kind: "iframe",
              policy: {
                allow_scripts: true,
                allow_forms: false,
                allow_fullscreen: true,
                allow_popups: false
              },
              preferred_size: capsule.preferred_size || { width: 720, height: 480 },
              sandbox_attributes: [
                "allow-scripts",
                "allow-same-origin",
                "allow-forms"
              ],
              csp: {
                "default-src": ["'self'"],
                "script-src": ["'self'", "'unsafe-inline'"],
                "style-src": ["'self'", "'unsafe-inline'"],
                "img-src": ["'self'", "data:", "https:"],
                "connect-src": capsule.sandbox_policy?.network?.allow || []
              }
            },
            expires_at: expiresAt,
            capsule_uri: `axp://capsules/${args.capsule_id}`,
            initial_params: args.params || {}
          }, null, 2)
        }
      ]
    };
  }
}
