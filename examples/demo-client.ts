#!/usr/bin/env tsx

/**
 * AXP Protocol Demo Client
 * Demonstrates how to interact with an AXP server
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";
import readline from "readline";
import chalk from "chalk";

// Types
interface SearchFilters {
  price?: { min?: number; max?: number };
  availability?: string[];
  intent?: string[];
  soft_min?: {
    uniqueness_score?: number;
    craftsmanship_score?: number;
    sustainability_score?: number;
    innovation_score?: number;
  };
}

class AXPDemoClient {
  private client: Client;
  private rl: readline.Interface;
  private connected = false;

  constructor() {
    this.client = new Client(
      {
        name: "axp-demo-client",
        version: "0.1.0",
      },
      {
        capabilities: {},
      }
    );

    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
  }

  async connect() {
    console.log(chalk.blue("🚀 Starting AXP MCP Server..."));
    
    const serverProcess = spawn("tsx", ["src/server/index.ts"], {
      stdio: ["pipe", "pipe", "inherit"],
      cwd: process.cwd(),
    });

    const transport = new StdioClientTransport({
      command: "tsx",
      args: ["src/server/index.ts"],
    });

    await this.client.connect(transport);
    this.connected = true;
    
    console.log(chalk.green("✅ Connected to AXP Server\n"));
  }

  async runDemo() {
    if (!this.connected) {
      await this.connect();
    }

    console.log(chalk.bold.cyan("=".repeat(60)));
    console.log(chalk.bold.cyan("         AXP Protocol Interactive Demo"));
    console.log(chalk.bold.cyan("=".repeat(60)));
    console.log();

    while (true) {
      const choice = await this.showMenu();
      
      switch (choice) {
        case "1":
          await this.getBrandProfile();
          break;
        case "2":
          await this.searchProducts();
          break;
        case "3":
          await this.getProductDetails();
          break;
        case "4":
          await this.exploreCapsule();
          break;
        case "5":
          await this.advancedSearch();
          break;
        case "6":
          await this.checkHealth();
          break;
        case "0":
          console.log(chalk.yellow("\n👋 Goodbye!"));
          this.rl.close();
          process.exit(0);
        default:
          console.log(chalk.red("Invalid choice. Please try again."));
      }
      
      await this.pause();
    }
  }

  private async showMenu(): Promise<string> {
    console.log(chalk.bold("\n📋 Main Menu:"));
    console.log("1. Get Brand Profile");
    console.log("2. Search Products");
    console.log("3. Get Product Details");
    console.log("4. Explore Experience Capsule");
    console.log("5. Advanced Search with Soft Signals");
    console.log("6. Check Server Health");
    console.log("0. Exit");
    
    return this.prompt("\nEnter your choice: ");
  }

  private async getBrandProfile() {
    console.log(chalk.blue("\n📊 Fetching Brand Profile..."));
    
    try {
      const result = await this.client.callTool("axp.getBrandProfile", {});
      const profile = JSON.parse(result.content[0].text);
      
      console.log(chalk.green("\n✨ Brand Profile:"));
      console.log(chalk.white(`Name: ${profile.brand.legal_name}`));
      console.log(chalk.white(`Founded: ${profile.brand.founded_year}`));
      console.log(chalk.white(`Employees: ${profile.brand.employee_count}`));
      console.log(chalk.white(`CSAT: ${(profile.brand.csat * 100).toFixed(1)}%`));
      console.log(chalk.white(`NPS: ${profile.brand.nps}`));
      
      console.log(chalk.yellow("\n🏆 Unique Value Props:"));
      profile.brand.unique_value_props?.forEach((prop: string) => {
        console.log(`  • ${prop}`);
      });
      
      console.log(chalk.cyan("\n⭐ Ratings:"));
      profile.brand.independent_ratings?.forEach((rating: any) => {
        console.log(`  • ${rating.source}: ${rating.score}/5 (${rating.reviews} reviews)`);
      });
    } catch (error) {
      console.error(chalk.red("Error fetching brand profile:"), error);
    }
  }

  private async searchProducts() {
    console.log(chalk.blue("\n🔍 Product Search"));
    
    const query = await this.prompt("Enter search query (or press Enter to see all): ");
    
    try {
      const result = await this.client.callTool("axp.searchCatalog", {
        query: query || undefined,
        limit: 5
      });
      
      const response = JSON.parse(result.content[0].text);
      
      if (response.items.length === 0) {
        console.log(chalk.yellow("No products found."));
        return;
      }
      
      console.log(chalk.green(`\n📦 Found ${response.items.length} products:\n`));
      
      response.items.forEach((product: any, index: number) => {
        console.log(chalk.bold(`${index + 1}. ${product.title}`));
        console.log(chalk.gray(`   ID: ${product.id}`));
        console.log(`   Price: €${product.price.value}`);
        console.log(`   Status: ${this.formatAvailability(product.availability.state)}`);
        
        if (product.soft_signals) {
          const signals = product.soft_signals;
          console.log(chalk.cyan("   Scores:"), 
            `Uniqueness: ${this.formatScore(signals.uniqueness_score)}`,
            `| Sustainability: ${this.formatScore(signals.sustainability_score)}`
          );
        }
        
        if (product.trust_signals?.review_summary) {
          const reviews = product.trust_signals.review_summary;
          console.log(chalk.yellow(`   Reviews: ⭐ ${reviews.avg_rating}/5 (${reviews.count_total} reviews)`));
        }
        console.log();
      });
    } catch (error) {
      console.error(chalk.red("Error searching products:"), error);
    }
  }

  private async getProductDetails() {
    const productId = await this.prompt("\nEnter product ID (e.g., sku_123): ");
    
    if (!productId) {
      console.log(chalk.yellow("Product ID required"));
      return;
    }
    
    console.log(chalk.blue(`\n📋 Fetching details for ${productId}...`));
    
    try {
      const result = await this.client.callTool("axp.getProduct", {
        product_id: productId
      });
      
      const { product } = JSON.parse(result.content[0].text);
      
      console.log(chalk.green("\n✨ Product Details:"));
      console.log(chalk.bold.white(`\n${product.title}`));
      console.log(chalk.gray(product.short_desc));
      console.log(`\nPrice: €${product.price.value}`);
      console.log(`Status: ${this.formatAvailability(product.availability.state)}`);
      
      if (product.tech_specs) {
        console.log(chalk.cyan("\n📐 Technical Specs:"));
        Object.entries(product.tech_specs).forEach(([key, value]) => {
          console.log(`  • ${this.formatKey(key)}: ${value}`);
        });
      }
      
      if (product.soft_signals) {
        console.log(chalk.yellow("\n📊 Quality Scores:"));
        const signals = product.soft_signals;
        console.log(`  • Uniqueness: ${this.formatScore(signals.uniqueness_score)}`);
        console.log(`  • Craftsmanship: ${this.formatScore(signals.craftsmanship_score)}`);
        console.log(`  • Sustainability: ${this.formatScore(signals.sustainability_score)}`);
        console.log(`  • Innovation: ${this.formatScore(signals.innovation_score)}`);
        
        if (signals.evidence?.length > 0) {
          console.log(chalk.green("\n🏆 Evidence:"));
          signals.evidence.forEach((e: any) => {
            console.log(`  • ${e.kind}: ${e.name}`);
          });
        }
      }
      
      if (product.experiences?.capsules?.length > 0) {
        console.log(chalk.magenta("\n🎮 Interactive Experiences:"));
        product.experiences.capsules.forEach((cap: any) => {
          console.log(`  • ${cap.title} (${cap.modality})`);
        });
      }
      
      if (product.intent_signals?.length > 0) {
        console.log(chalk.blue("\n🎯 Customer Intent:"));
        product.intent_signals.forEach((intent: any) => {
          console.log(`  • ${this.formatKey(intent.intent)}: ${(intent.share * 100).toFixed(0)}%`);
        });
      }
    } catch (error: any) {
      if (error.message?.includes("not found")) {
        console.log(chalk.red(`Product ${productId} not found`));
      } else {
        console.error(chalk.red("Error fetching product:"), error);
      }
    }
  }

  private async exploreCapsule() {
    const capsuleId = await this.prompt("\nEnter capsule ID (e.g., cap_sneaker_3d): ");
    
    if (!capsuleId) {
      console.log(chalk.yellow("Capsule ID required"));
      return;
    }
    
    console.log(chalk.blue(`\n🎮 Exploring capsule ${capsuleId}...`));
    
    try {
      const result = await this.client.callTool("axp.getCapsule", {
        capsule_id: capsuleId
      });
      
      const capsule = JSON.parse(result.content[0].text);
      
      console.log(chalk.green("\n✨ Experience Capsule Configuration:"));
      console.log(`URI: ${capsule.capsule_uri}`);
      console.log(`Type: ${capsule.sandbox_embed.kind}`);
      console.log(`Size: ${capsule.sandbox_embed.preferred_size.width}x${capsule.sandbox_embed.preferred_size.height}`);
      
      console.log(chalk.yellow("\n🔒 Security Policy:"));
      const policy = capsule.sandbox_embed.policy;
      console.log(`  • Scripts: ${policy.allow_scripts ? '✅ Allowed' : '❌ Blocked'}`);
      console.log(`  • Forms: ${policy.allow_forms ? '✅ Allowed' : '❌ Blocked'}`);
      console.log(`  • Fullscreen: ${policy.allow_fullscreen ? '✅ Allowed' : '❌ Blocked'}`);
      
      console.log(chalk.cyan("\n💡 To embed this capsule in your application:"));
      console.log(chalk.gray("1. Create an iframe with the capsule URI"));
      console.log(chalk.gray("2. Apply the security policy"));
      console.log(chalk.gray("3. Setup PostMessage communication"));
      console.log(chalk.gray("4. Handle add_to_cart and state_changed events"));
    } catch (error: any) {
      if (error.message?.includes("not found")) {
        console.log(chalk.red(`Capsule ${capsuleId} not found`));
      } else {
        console.error(chalk.red("Error fetching capsule:"), error);
      }
    }
  }

  private async advancedSearch() {
    console.log(chalk.blue("\n🔍 Advanced Search with Soft Signals"));
    
    const query = await this.prompt("Search query (optional): ");
    const minUniqueness = await this.prompt("Minimum uniqueness score (0-1, optional): ");
    const minSustainability = await this.prompt("Minimum sustainability score (0-1, optional): ");
    const intent = await this.prompt("Customer intent (e.g., fashion, sport, travel): ");
    
    const filters: SearchFilters = {};
    
    if (minUniqueness || minSustainability) {
      filters.soft_min = {};
      if (minUniqueness) filters.soft_min.uniqueness_score = parseFloat(minUniqueness);
      if (minSustainability) filters.soft_min.sustainability_score = parseFloat(minSustainability);
    }
    
    if (intent) {
      filters.intent = [intent];
    }
    
    try {
      const result = await this.client.callTool("axp.searchCatalog", {
        query: query || undefined,
        filters: Object.keys(filters).length > 0 ? filters : undefined,
        limit: 10
      });
      
      const response = JSON.parse(result.content[0].text);
      
      if (response.items.length === 0) {
        console.log(chalk.yellow("\nNo products match your criteria."));
        return;
      }
      
      console.log(chalk.green(`\n✨ Found ${response.items.length} matching products:\n`));
      
      response.items.forEach((product: any) => {
        console.log(chalk.bold(`• ${product.title}`));
        
        if (product.soft_signals) {
          const scores = [];
          if (product.soft_signals.uniqueness_score !== undefined) {
            scores.push(`Unique: ${this.formatScore(product.soft_signals.uniqueness_score)}`);
          }
          if (product.soft_signals.sustainability_score !== undefined) {
            scores.push(`Sustainable: ${this.formatScore(product.soft_signals.sustainability_score)}`);
          }
          if (scores.length > 0) {
            console.log(chalk.cyan(`  ${scores.join(" | ")}`));
          }
        }
      });
    } catch (error) {
      console.error(chalk.red("Error performing advanced search:"), error);
    }
  }

  private async checkHealth() {
    console.log(chalk.blue("\n🏥 Checking server health..."));
    
    try {
      const result = await this.client.callTool("axp.health", {});
      const health = JSON.parse(result.content[0].text);
      
      console.log(chalk.green("\n✅ Server Health:"));
      console.log(`Status: ${health.status === 'ok' ? chalk.green(health.status) : chalk.red(health.status)}`);
      console.log(`Version: ${health.version}`);
      console.log(`Uptime: ${Math.floor(health.uptime / 60)} minutes`);
      console.log(`Timestamp: ${new Date(health.timestamp).toLocaleString()}`);
    } catch (error) {
      console.error(chalk.red("Error checking health:"), error);
    }
  }

  private formatAvailability(state: string): string {
    const colors: Record<string, any> = {
      in_stock: chalk.green,
      out_of_stock: chalk.red,
      preorder: chalk.yellow,
      discontinued: chalk.gray
    };
    
    const labels: Record<string, string> = {
      in_stock: "✅ In Stock",
      out_of_stock: "❌ Out of Stock",
      preorder: "📅 Preorder",
      discontinued: "⛔ Discontinued"
    };
    
    const color = colors[state] || chalk.white;
    const label = labels[state] || state;
    
    return color(label);
  }

  private formatScore(score?: number): string {
    if (score === undefined) return "N/A";
    
    const percentage = Math.round(score * 100);
    const bars = Math.round(score * 10);
    const filled = "█".repeat(bars);
    const empty = "░".repeat(10 - bars);
    
    let color = chalk.red;
    if (percentage >= 80) color = chalk.green;
    else if (percentage >= 60) color = chalk.yellow;
    
    return color(`${filled}${empty} ${percentage}%`);
  }

  private formatKey(key: string): string {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  private prompt(question: string): Promise<string> {
    return new Promise((resolve) => {
      this.rl.question(chalk.cyan(question), resolve);
    });
  }

  private pause(): Promise<void> {
    return new Promise((resolve) => {
      this.rl.question(chalk.gray("\nPress Enter to continue..."), () => resolve());
    });
  }
}

// Run the demo
async function main() {
  const client = new AXPDemoClient();
  
  try {
    await client.runDemo();
  } catch (error) {
    console.error(chalk.red("Fatal error:"), error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on("SIGINT", () => {
  console.log(chalk.yellow("\n\n👋 Shutting down gracefully..."));
  process.exit(0);
});

// Check if chalk is installed
try {
  require.resolve("chalk");
} catch {
  console.log("Installing required dependency: chalk");
  require("child_process").execSync("npm install chalk", { stdio: "inherit" });
}

main();
