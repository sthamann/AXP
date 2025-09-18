"""
AXP Protocol Pydantic Models
Version: 0.1.0
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator, conint, confloat


# ============================================================================
# Enums
# ============================================================================

class TrustBadge(str, Enum):
    PCI_DSS_READY = "PCI DSS ready"
    GDPR_CONTROLS = "GDPR controls"
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"


class AvailabilityState(str, Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    PREORDER = "preorder"
    DISCONTINUED = "discontinued"


class CapsuleModality(str, Enum):
    CANVAS3D = "canvas3d"
    HTML = "html"
    AR = "ar"
    VR = "vr"
    CONFIGURATOR = "configurator"


class EvidenceKind(str, Enum):
    CERTIFICATION = "certification"
    AWARD = "award"
    AUDIT_REPORT = "audit_report"
    LAB_TEST = "lab_test"
    PRESS_MENTION = "press_mention"


class ReturnReasonType(str, Enum):
    SIZE_ISSUE = "size_issue"
    DAMAGED = "damaged"
    COLOR_MISMATCH = "color_mismatch"
    QUALITY_EXPECTATION = "quality_expectation"
    CHANGED_MIND = "changed_mind"
    SHIPPING_DELAY = "shipping_delay"


class CustomerIntent(str, Enum):
    GIFT = "gift"
    DAILY_COMMUTE = "daily_commute"
    HOBBY = "hobby"
    PROFESSIONAL_USE = "professional_use"
    TRAVEL = "travel"
    FASHION = "fashion"
    SPORT = "sport"
    BASKETBALL = "basketball"


class StorageType(str, Enum):
    NONE = "none"
    MEMORY = "memory"
    SESSION = "session"


class BrowserPermission(str, Enum):
    CAMERA = "camera"
    MICROPHONE = "microphone"
    GEOLOCATION = "geolocation"
    NOTIFICATIONS = "notifications"
    CLIPBOARD = "clipboard"


class SignatureAlgorithm(str, Enum):
    RS256 = "RS256"
    ES256 = "ES256"
    EdDSA = "EdDSA"


class AgentRole(str, Enum):
    BRAND = "brand"
    CATALOG = "catalog"
    EXPERIENCE_PROVIDER = "experience_provider"


# ============================================================================
# Common Models
# ============================================================================

class Signature(BaseModel):
    alg: SignatureAlgorithm
    kid: Optional[str] = None
    value: str = Field(..., description="Base64url encoded signature")


class LocalizedText(BaseModel):
    lang: str = Field(..., pattern="^[a-z]{2}$")
    text: str


# ============================================================================
# Brand Profile Models
# ============================================================================

class IndependentRating(BaseModel):
    source: str
    score: confloat(ge=0, le=5)
    reviews: Optional[int] = Field(None, ge=0)
    url: Optional[HttpUrl] = None


class ServiceSLA(BaseModel):
    first_response_hours: Optional[float] = Field(None, ge=0)
    resolution_hours_p50: Optional[float] = Field(None, ge=0)


class Warranty(BaseModel):
    name: str
    duration_days: int = Field(..., ge=0)


class TrustFactors(BaseModel):
    badges: Optional[List[TrustBadge]] = None
    warranties: Optional[List[Warranty]] = None
    data_provenance: Optional[str] = None


class Brand(BaseModel):
    id: str
    legal_name: str
    founded_year: Optional[conint(ge=1800, le=2100)] = None
    employee_count: Optional[int] = Field(None, ge=0)
    customer_count_estimate: Optional[int] = Field(None, ge=0)
    headquarters_country: Optional[str] = Field(None, pattern="^[A-Z]{2}$")
    domains: List[str]
    certifications: Optional[List[str]] = None
    independent_ratings: Optional[List[IndependentRating]] = None
    csat: Optional[confloat(ge=0, le=1)] = None
    nps: Optional[conint(ge=-100, le=100)] = None
    return_rate: Optional[confloat(ge=0, le=1)] = None
    service_sla: Optional[ServiceSLA] = None
    unique_value_props: Optional[List[str]] = None
    trust_factors: Optional[TrustFactors] = None


class BrandProfile(BaseModel):
    spec: Literal["axp"] = "axp"
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    generated_at: datetime
    brand: Brand
    signature: Optional[Signature] = None


# ============================================================================
# Product Models
# ============================================================================

class Price(BaseModel):
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    value: float = Field(..., ge=0)


class Availability(BaseModel):
    state: AvailabilityState
    quantity: Optional[int] = Field(None, ge=0)


class ImageEmbeddings(BaseModel):
    clip: Optional[Dict[str, Any]] = None


class MediaImage(BaseModel):
    url: HttpUrl
    machine_captions: Optional[List[LocalizedText]] = None
    embeddings: Optional[ImageEmbeddings] = None


class MediaDocument(BaseModel):
    url: HttpUrl
    semantic_summary: Optional[LocalizedText] = None
    checksum_sha256: Optional[str] = Field(None, pattern="^[a-f0-9]{64}$")


class Media(BaseModel):
    images: Optional[List[MediaImage]] = None
    documents: Optional[List[MediaDocument]] = None


class ExperienceCapsuleRef(BaseModel):
    id: str
    title: str
    capsule_uri: str
    modality: CapsuleModality
    preferred_size: Optional[Dict[str, int]] = None
    params_schema: Optional[Dict[str, Any]] = None


class DemoVideo(BaseModel):
    url: HttpUrl
    caption: Optional[str] = None


class Experiences(BaseModel):
    capsules: Optional[List[ExperienceCapsuleRef]] = None
    demo_videos: Optional[List[DemoVideo]] = None


class Evidence(BaseModel):
    kind: EvidenceKind
    name: str
    url: Optional[HttpUrl] = None


class SoftSignals(BaseModel):
    uniqueness_score: Optional[confloat(ge=0, le=1)] = None
    craftsmanship_score: Optional[confloat(ge=0, le=1)] = None
    sustainability_score: Optional[confloat(ge=0, le=1)] = None
    innovation_score: Optional[confloat(ge=0, le=1)] = None
    evidence: Optional[List[Evidence]] = None


class ReviewSummary(BaseModel):
    avg_rating: Optional[confloat(ge=0, le=5)] = None
    count_total: Optional[int] = Field(None, ge=0)
    top_positive: Optional[List[str]] = None
    top_negative: Optional[List[str]] = None


class ReturnReason(BaseModel):
    reason: ReturnReasonType
    share: confloat(ge=0, le=1)


class ProductTrustSignals(BaseModel):
    review_summary: Optional[ReviewSummary] = None
    return_reasons: Optional[List[ReturnReason]] = None
    return_rate: Optional[confloat(ge=0, le=1)] = None
    warranty_days: Optional[int] = Field(None, ge=0)


class IntentSignal(BaseModel):
    intent: CustomerIntent
    share: confloat(ge=0, le=1)


class ShippingPolicy(BaseModel):
    regions: Optional[List[str]] = Field(None, description="ISO country codes")
    days: Optional[int] = Field(None, ge=0)


class ReturnPolicy(BaseModel):
    days: Optional[int] = Field(None, ge=0)
    restocking_fee: Optional[float] = Field(None, ge=0)


class Policies(BaseModel):
    shipping: Optional[ShippingPolicy] = None
    returns: Optional[ReturnPolicy] = None


class Provenance(BaseModel):
    brand_id: str
    last_verified: datetime
    signature: Optional[str] = None


class AgentRankingHint(BaseModel):
    primary: Optional[List[str]] = None
    secondary: Optional[List[str]] = None


class TechSpecs(BaseModel):
    material: Optional[str] = None
    weight_grams: Optional[float] = Field(None, ge=0)
    sizes: Optional[List[str]] = None
    care: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields


class Product(BaseModel):
    id: str
    parent_id: Optional[str] = None
    title: str
    short_desc: Optional[str] = Field(None, max_length=200)
    tech_specs: Optional[TechSpecs] = None
    price: Price
    availability: Availability
    media: Optional[Media] = None
    experiences: Optional[Experiences] = None
    soft_signals: Optional[SoftSignals] = None
    trust_signals: Optional[ProductTrustSignals] = None
    intent_signals: Optional[List[IntentSignal]] = None
    policies: Optional[Policies] = None
    provenance: Optional[Provenance] = None
    agent_ranking_hint: Optional[AgentRankingHint] = None


class ProductWrapper(BaseModel):
    product: Product


# ============================================================================
# Review Models
# ============================================================================

class ReviewAspects(BaseModel):
    comfort: Optional[confloat(ge=0, le=1)] = None
    build: Optional[confloat(ge=0, le=1)] = None
    style: Optional[confloat(ge=0, le=1)] = None
    value: Optional[confloat(ge=0, le=1)] = None
    durability: Optional[confloat(ge=0, le=1)] = None
    fit: Optional[confloat(ge=0, le=1)] = None
    
    class Config:
        extra = "allow"  # Allow additional aspect scores


class Review(BaseModel):
    product_id: str
    source: str
    rating: conint(ge=1, le=5)
    title: Optional[str] = Field(None, max_length=100)
    text: Optional[str] = Field(None, max_length=5000)
    lang: Optional[str] = Field(None, pattern="^[a-z]{2}$")
    verified_purchase: Optional[bool] = None
    timestamp: datetime
    aspects: Optional[ReviewAspects] = None
    helpful_votes: Optional[int] = Field(None, ge=0)
    total_votes: Optional[int] = Field(None, ge=0)


# ============================================================================
# Experience Capsule Models
# ============================================================================

class CapsuleEntry(BaseModel):
    html: Optional[str] = None
    js: Optional[str] = None
    
    @validator("html", "js")
    def at_least_one_entry(cls, v, values):
        if not v and not any(values.values()):
            raise ValueError("At least one entry point (html or js) is required")
        return v


class NetworkPolicy(BaseModel):
    allow: Optional[List[str]] = None
    block_all_others: bool


class SandboxPolicy(BaseModel):
    dom: bool
    storage: StorageType
    network: NetworkPolicy
    lifetime_seconds: conint(ge=1, le=3600)
    permissions: Optional[List[BrowserPermission]] = None


class CapsuleAPI(BaseModel):
    inbound_events: List[str]
    outbound_events: List[str]


class CapsuleResources(BaseModel):
    max_memory_mb: Optional[conint(ge=1, le=512)] = 128
    max_cpu_percent: Optional[conint(ge=1, le=100)] = 25


class ExperienceCapsule(BaseModel):
    id: str
    name: str
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    entry: CapsuleEntry
    surfaces: List[CapsuleModality] = Field(..., min_items=1)
    sandbox_policy: SandboxPolicy
    api: CapsuleAPI
    resources: Optional[CapsuleResources] = None
    signature: Optional[Signature] = None


# ============================================================================
# Export Bundle Models
# ============================================================================

class Publisher(BaseModel):
    name: str
    domain: str
    public_keys: Optional[List[str]] = None


class ExportFiles(BaseModel):
    catalog_products: str
    experiences: Optional[str] = None
    policies: Optional[str] = None
    ratings_reviews: Optional[str] = None


class ExportManifest(BaseModel):
    spec: Literal["axp"] = "axp"
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    publisher: Publisher
    brand_profile: str
    files: ExportFiles
    generated_at: datetime
    signature: Optional[Signature] = None


# ============================================================================
# MCP Tool Models
# ============================================================================

class PriceRange(BaseModel):
    min: Optional[float] = Field(None, ge=0)
    max: Optional[float] = Field(None, ge=0)


class SoftMinFilters(BaseModel):
    uniqueness_score: Optional[confloat(ge=0, le=1)] = None
    craftsmanship_score: Optional[confloat(ge=0, le=1)] = None
    sustainability_score: Optional[confloat(ge=0, le=1)] = None
    innovation_score: Optional[confloat(ge=0, le=1)] = None


class SearchFilters(BaseModel):
    price: Optional[PriceRange] = None
    availability: Optional[List[AvailabilityState]] = None
    intent: Optional[List[CustomerIntent]] = None
    soft_min: Optional[SoftMinFilters] = None


class SearchCatalogInput(BaseModel):
    query: Optional[str] = None
    filters: Optional[SearchFilters] = None
    limit: Optional[conint(ge=1, le=100)] = 20
    cursor: Optional[str] = None


class SearchCatalogOutput(BaseModel):
    items: List[Product]
    next_cursor: Optional[str] = None


class GetProductInput(BaseModel):
    product_id: str


class GetExportInput(BaseModel):
    since: Optional[datetime] = None


class GetExportOutput(BaseModel):
    bundle_uri: str
    checksum_sha256: str
    expires_at: datetime


class GetCapsuleInput(BaseModel):
    capsule_id: str


class SandboxEmbed(BaseModel):
    kind: Literal["iframe"] = "iframe"
    policy: Dict[str, bool]
    preferred_size: Optional[Dict[str, int]] = None


class GetCapsuleOutput(BaseModel):
    capsule_uri: str
    sandbox_embed: SandboxEmbed


class SubscribeInventoryInput(BaseModel):
    product_ids: List[str] = Field(..., min_items=1, max_items=100)


class SubscribeInventoryOutput(BaseModel):
    subscription_id: str
    ttl_seconds: int


class InventoryUpdateEvent(BaseModel):
    type: Literal["inventory_update"] = "inventory_update"
    product_id: str
    availability: Availability


class HealthOutput(BaseModel):
    status: Literal["ok", "degraded", "error"]
    version: str


# ============================================================================
# Error Models
# ============================================================================

class AXPErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class AXPError(BaseModel):
    error: AXPErrorDetail


# ============================================================================
# A2A Extension Models
# ============================================================================

class AgentCardExtension(BaseModel):
    uri: Literal["https://agentic-commerce.org/axp/v0.1"]
    required: bool
    params: Dict[str, List[AgentRole]]
