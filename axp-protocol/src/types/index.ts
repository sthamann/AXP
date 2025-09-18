/**
 * AXP Protocol Type Definitions
 * @version 0.1.0
 */

// ============================================================================
// Brand Profile Types
// ============================================================================

export interface BrandProfile {
  spec: "axp";
  version: string;
  generated_at: string;
  brand: Brand;
  signature?: Signature;
}

export interface Brand {
  id: string;
  legal_name: string;
  founded_year?: number;
  employee_count?: number;
  customer_count_estimate?: number;
  headquarters_country?: string;
  domains: string[];
  certifications?: string[];
  independent_ratings?: IndependentRating[];
  csat?: number;
  nps?: number;
  return_rate?: number;
  service_sla?: ServiceSLA;
  unique_value_props?: string[];
  trust_factors?: TrustFactors;
}

export interface IndependentRating {
  source: string;
  score: number;
  reviews?: number;
  url?: string;
}

export interface ServiceSLA {
  first_response_hours?: number;
  resolution_hours_p50?: number;
}

export interface TrustFactors {
  badges?: TrustBadge[];
  warranties?: Warranty[];
  data_provenance?: string;
}

export type TrustBadge = "PCI DSS ready" | "GDPR controls" | "SOC2" | "ISO27001";

export interface Warranty {
  name: string;
  duration_days: number;
}

// ============================================================================
// Product Types
// ============================================================================

export interface ProductWrapper {
  product: Product;
}

export interface Product {
  id: string;
  parent_id?: string | null;
  title: string;
  short_desc?: string;
  tech_specs?: TechSpecs;
  price: Price;
  availability: Availability;
  media?: Media;
  experiences?: Experiences;
  soft_signals?: SoftSignals;
  trust_signals?: ProductTrustSignals;
  intent_signals?: IntentSignal[];
  policies?: Policies;
  provenance?: Provenance;
  agent_ranking_hint?: AgentRankingHint;
}

export interface TechSpecs {
  material?: string;
  weight_grams?: number;
  sizes?: string[];
  care?: string;
  [key: string]: any;
}

export interface Price {
  currency: string;
  value: number;
}

export interface Availability {
  state: "in_stock" | "out_of_stock" | "preorder" | "discontinued";
  quantity?: number;
}

export interface Media {
  images?: MediaImage[];
  documents?: MediaDocument[];
}

export interface MediaImage {
  url: string;
  machine_captions?: MachineCaption[];
  embeddings?: ImageEmbeddings;
}

export interface MachineCaption {
  lang: string;
  text: string;
}

export interface ImageEmbeddings {
  clip?: {
    dim: number;
    vector: string; // Base64 encoded float array
  };
}

export interface MediaDocument {
  url: string;
  semantic_summary?: {
    lang: string;
    text: string;
  };
  checksum_sha256?: string;
}

export interface Experiences {
  capsules?: ExperienceCapsuleRef[];
  demo_videos?: DemoVideo[];
}

export interface ExperienceCapsuleRef {
  id: string;
  title: string;
  capsule_uri: string;
  modality: CapsuleModality;
  preferred_size?: {
    width: number;
    height: number;
  };
  params_schema?: any; // JSON Schema object
}

export type CapsuleModality = "canvas3d" | "html" | "ar" | "vr" | "configurator";

export interface DemoVideo {
  url: string;
  caption?: string;
}

export interface SoftSignals {
  uniqueness_score?: number;
  craftsmanship_score?: number;
  sustainability_score?: number;
  innovation_score?: number;
  evidence?: Evidence[];
}

export interface Evidence {
  kind: EvidenceKind;
  name: string;
  url?: string;
}

export type EvidenceKind = "certification" | "award" | "audit_report" | "lab_test" | "press_mention";

export interface ProductTrustSignals {
  review_summary?: ReviewSummary;
  return_reasons?: ReturnReason[];
  return_rate?: number;
  warranty_days?: number;
}

export interface ReviewSummary {
  avg_rating?: number;
  count_total?: number;
  top_positive?: string[];
  top_negative?: string[];
}

export interface ReturnReason {
  reason: ReturnReasonType;
  share: number;
}

export type ReturnReasonType = 
  | "size_issue" 
  | "damaged" 
  | "color_mismatch" 
  | "quality_expectation" 
  | "changed_mind" 
  | "shipping_delay";

export interface IntentSignal {
  intent: CustomerIntent;
  share: number;
}

export type CustomerIntent = 
  | "gift" 
  | "daily_commute" 
  | "hobby" 
  | "professional_use" 
  | "travel" 
  | "fashion"
  | "sport"
  | "basketball";

export interface Policies {
  shipping?: ShippingPolicy;
  returns?: ReturnPolicy;
}

export interface ShippingPolicy {
  regions?: string[];
  days?: number;
}

export interface ReturnPolicy {
  days?: number;
  restocking_fee?: number;
}

export interface Provenance {
  brand_id: string;
  last_verified: string;
  signature?: string;
}

export interface AgentRankingHint {
  primary?: string[];
  secondary?: string[];
}

// ============================================================================
// Review Types
// ============================================================================

export interface Review {
  product_id: string;
  source: string;
  rating: number;
  title?: string;
  text?: string;
  lang?: string;
  verified_purchase?: boolean;
  timestamp: string;
  aspects?: ReviewAspects;
  helpful_votes?: number;
  total_votes?: number;
}

export interface ReviewAspects {
  comfort?: number;
  build?: number;
  style?: number;
  value?: number;
  durability?: number;
  fit?: number;
  [key: string]: number | undefined;
}

// ============================================================================
// Experience Capsule Types
// ============================================================================

export interface ExperienceCapsule {
  id: string;
  name: string;
  version: string;
  entry: CapsuleEntry;
  surfaces: CapsuleModality[];
  sandbox_policy: SandboxPolicy;
  api: CapsuleAPI;
  resources?: CapsuleResources;
  signature?: Signature;
}

export interface CapsuleEntry {
  html?: string;
  js?: string;
}

export interface SandboxPolicy {
  dom: boolean;
  storage: "none" | "memory" | "session";
  network: NetworkPolicy;
  lifetime_seconds: number;
  permissions?: BrowserPermission[];
}

export interface NetworkPolicy {
  allow?: string[];
  block_all_others: boolean;
}

export type BrowserPermission = 
  | "camera" 
  | "microphone" 
  | "geolocation" 
  | "notifications" 
  | "clipboard";

export interface CapsuleAPI {
  inbound_events: string[];
  outbound_events: string[];
}

export interface CapsuleResources {
  max_memory_mb?: number;
  max_cpu_percent?: number;
}

// ============================================================================
// Capsule Communication Types
// ============================================================================

export type InboundCapsuleEvent =
  | { type: "init"; correlationId: string }
  | { type: "configure"; params: Record<string, unknown> }
  | { type: "set_variant"; sku: string; params: Record<string, unknown> }
  | { type: "request_quote" };

export type OutboundCapsuleEvent =
  | { type: "ready" }
  | { type: "state_changed"; state: Record<string, unknown> }
  | { type: "add_to_cart"; sku: string; quantity: number }
  | { type: "telemetry"; event: string; data: Record<string, unknown> };

// ============================================================================
// Export Bundle Types
// ============================================================================

export interface ExportManifest {
  spec: "axp";
  version: string;
  publisher: Publisher;
  brand_profile: string;
  files: ExportFiles;
  generated_at: string;
  signature?: Signature;
}

export interface Publisher {
  name: string;
  domain: string;
  public_keys?: string[];
}

export interface ExportFiles {
  catalog_products: string;
  experiences?: string;
  policies?: string;
  ratings_reviews?: string;
}

// ============================================================================
// MCP Tool Types
// ============================================================================

export interface SearchCatalogInput {
  query?: string;
  filters?: SearchFilters;
  limit?: number;
  cursor?: string;
}

export interface SearchFilters {
  price?: PriceRange;
  availability?: Availability["state"][];
  intent?: CustomerIntent[];
  soft_min?: {
    uniqueness_score?: number;
    craftsmanship_score?: number;
    sustainability_score?: number;
    innovation_score?: number;
  };
}

export interface PriceRange {
  min?: number;
  max?: number;
}

export interface SearchCatalogOutput {
  items: Product[];
  next_cursor?: string;
}

export interface GetProductInput {
  product_id: string;
}

export interface GetExportInput {
  since?: string;
}

export interface GetExportOutput {
  bundle_uri: string;
  checksum_sha256: string;
  expires_at: string;
}

export interface GetCapsuleInput {
  capsule_id: string;
}

export interface GetCapsuleOutput {
  capsule_uri: string;
  sandbox_embed: SandboxEmbed;
}

export interface SandboxEmbed {
  kind: "iframe";
  policy: {
    allow_scripts: boolean;
    allow_forms: boolean;
    allow_fullscreen: boolean;
  };
  preferred_size?: {
    width: number;
    height: number;
  };
}

export interface SubscribeInventoryInput {
  product_ids: string[];
}

export interface SubscribeInventoryOutput {
  subscription_id: string;
  ttl_seconds: number;
}

export interface InventoryUpdateEvent {
  type: "inventory_update";
  product_id: string;
  availability: Availability;
}

export interface HealthOutput {
  status: "ok" | "degraded" | "error";
  version: string;
}

// ============================================================================
// Common Types
// ============================================================================

export interface Signature {
  alg: "RS256" | "ES256" | "EdDSA";
  kid?: string;
  value: string;
}

export interface AXPError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

// ============================================================================
// A2A Extension Types
// ============================================================================

export interface AgentCardExtension {
  uri: "https://agentic-commerce.org/axp/v0.1";
  required: boolean;
  params: {
    roles: AgentRole[];
  };
}

export type AgentRole = "brand" | "catalog" | "experience_provider";

// ============================================================================
// Export all types
// ============================================================================

export * from "./generated"; // Include auto-generated types from JSON Schema
