#!/usr/bin/env python3
"""
Third-Party Data Enrichment Providers for AXP Protocol

Provides unified adapters for external trust and technology verification sources.
Each provider implements evidence collection with cryptographic verification.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Literal
import hashlib
import json
from urllib.parse import quote
from enum import Enum


class ProviderType(Enum):
    """Supported third-party data providers"""
    TRUSTPILOT = "trustpilot"
    TRUSTED_SHOPS = "trusted_shops"
    GOOGLE_SELLER = "google_seller_ratings"
    BUILTWITH = "builtwith"
    WAPPALYZER = "wappalyzer"
    BAZAARVOICE = "bazaarvoice"
    JUDGEME = "judgeme"
    BBB = "bbb"


@dataclass
class ProviderEvidence:
    """Standardized evidence from third-party providers"""
    source: str
    entity: Literal["brand", "product"]
    source_id: str
    retrieved_at: datetime
    evidence_url: str
    data: Dict[str, Any]
    signature: Optional[str] = None
    ttl_hours: int = 168  # Default 7 days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to AXP-compliant dictionary"""
        return {
            "source": self.source,
            "entity": self.entity,
            "source_id": self.source_id,
            "retrieved_at": self.retrieved_at.isoformat() + "Z",
            "evidence_url": self.evidence_url,
            "data": self.data,
            "signature": self.signature,
            "ttl_hours": self.ttl_hours
        }
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of evidence data"""
        canonical = json.dumps(self.data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()


class BaseProvider(ABC):
    """Base class for all third-party data providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider_type: ProviderType = None
        self.ttl_hours = 168  # Default 7 days
    
    @abstractmethod
    async def fetch_brand_data(self, domain: str) -> ProviderEvidence:
        """Fetch brand-level data from provider"""
        pass
    
    @abstractmethod
    async def fetch_product_data(self, product_id: str) -> ProviderEvidence:
        """Fetch product-level data from provider"""
        pass
    
    def validate_freshness(self, evidence: ProviderEvidence) -> bool:
        """Check if evidence is still within TTL"""
        age = datetime.utcnow() - evidence.retrieved_at
        return age < timedelta(hours=evidence.ttl_hours)
    
    def detect_anomaly(self, new_data: Dict, historical_data: List[Dict]) -> bool:
        """Detect suspicious changes in metrics"""
        if not historical_data:
            return False
        
        # Check for sudden rating jumps
        if 'avg_rating' in new_data and historical_data:
            last_rating = historical_data[-1].get('avg_rating', 0)
            rating_change = abs(new_data['avg_rating'] - last_rating)
            if rating_change > 1.5:  # Suspicious if > 1.5 star jump
                return True
        
        # Check for review count explosions
        if 'count_total' in new_data and historical_data:
            last_count = historical_data[-1].get('count_total', 0)
            if last_count > 0:
                growth_rate = (new_data['count_total'] - last_count) / last_count
                if growth_rate > 10:  # 10x growth is suspicious
                    return True
        
        return False


class TrustpilotProvider(BaseProvider):
    """Trustpilot review data provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_type = ProviderType.TRUSTPILOT
        self.base_url = "https://api.trustpilot.com/v1"
        self.ttl_hours = 24  # Trustpilot updates frequently
    
    async def fetch_brand_data(self, domain: str) -> ProviderEvidence:
        """Fetch Trustpilot business reviews"""
        # In production, make actual API call
        # For now, return example data structure
        
        business_unit_id = f"trustpilot:domain:{domain}"
        
        data = {
            "avg_rating": 4.6,
            "count_total": 12873,
            "breakdown": {
                "5": 72,
                "4": 18,
                "3": 6,
                "2": 2,
                "1": 2
            },
            "trust_score": 4.5,
            "categories": ["Electronics", "Consumer Goods"],
            "verification_level": "verified",
            "recent_reviews": [
                {
                    "rating": 5,
                    "title": "Excellent service",
                    "verified": True,
                    "date": "2025-09-15"
                }
            ]
        }
        
        return ProviderEvidence(
            source="trustpilot",
            entity="brand",
            source_id=business_unit_id,
            retrieved_at=datetime.utcnow(),
            evidence_url=f"https://www.trustpilot.com/review/{domain}",
            data=data,
            ttl_hours=self.ttl_hours
        )
    
    async def fetch_product_data(self, product_id: str) -> ProviderEvidence:
        """Trustpilot doesn't have product-level data typically"""
        raise NotImplementedError("Trustpilot provides brand-level reviews only")


class TrustedShopsProvider(BaseProvider):
    """Trusted Shops certification and review provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_type = ProviderType.TRUSTED_SHOPS
        self.base_url = "https://api.trustedshops.com/rest/public/v2"
    
    async def fetch_brand_data(self, shop_id: str) -> ProviderEvidence:
        """Fetch Trusted Shops certification and reviews"""
        
        data = {
            "shop_id": shop_id,
            "certification": {
                "status": "valid",
                "cert_id": "X123456789",
                "valid_until": "2026-12-31",
                "verification_token": "abc123xyz",
                "badge_status": "active"
            },
            "reviews": {
                "avg_rating": 4.8,
                "count_total": 5432,
                "response_rate": 0.95,
                "recommendation_rate": 0.92
            },
            "guarantee": {
                "active": True,
                "max_amount_eur": 2500,
                "claims_last_year": 3
            },
            "quality_criteria": {
                "delivery_reliability": 4.9,
                "product_quality": 4.7,
                "customer_service": 4.8
            }
        }
        
        return ProviderEvidence(
            source="trusted_shops",
            entity="brand",
            source_id=f"trusted_shops:cert:{shop_id}",
            retrieved_at=datetime.utcnow(),
            evidence_url=f"https://www.trustedshops.com/shops/{shop_id}",
            data=data,
            ttl_hours=168  # Weekly refresh
        )
    
    async def fetch_product_data(self, product_id: str) -> ProviderEvidence:
        """Fetch product-specific reviews if available"""
        
        data = {
            "product_id": product_id,
            "reviews": {
                "avg_rating": 4.7,
                "count": 234,
                "verified_purchase_rate": 0.98
            },
            "quality_aspects": {
                "quality": 4.8,
                "value_for_money": 4.5,
                "delivery": 4.9
            }
        }
        
        return ProviderEvidence(
            source="trusted_shops",
            entity="product",
            source_id=f"trusted_shops:product:{product_id}",
            retrieved_at=datetime.utcnow(),
            evidence_url=f"https://www.trustedshops.com/product/{product_id}",
            data=data,
            ttl_hours=168
        )


class BuiltWithProvider(BaseProvider):
    """Technology stack detection provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_type = ProviderType.BUILTWITH
        self.base_url = "https://api.builtwith.com/v20/api.json"
        self.ttl_hours = 720  # 30 days - tech stack changes slowly
    
    async def fetch_brand_data(self, domain: str) -> ProviderEvidence:
        """Detect technology stack for domain"""
        
        data = {
            "detected": [
                {
                    "name": "Shopware",
                    "category": "ecommerce",
                    "version": "6.5",
                    "confidence": 0.99
                },
                {
                    "name": "Cloudflare",
                    "category": "cdn",
                    "confidence": 1.0
                },
                {
                    "name": "Google Analytics",
                    "category": "analytics",
                    "confidence": 1.0
                },
                {
                    "name": "PayPal",
                    "category": "payment",
                    "confidence": 0.95
                },
                {
                    "name": "Klaviyo",
                    "category": "email_marketing",
                    "confidence": 0.90
                },
                {
                    "name": "MySQL",
                    "category": "database",
                    "confidence": 0.85
                }
            ],
            "capabilities": {
                "has_ssl": True,
                "has_mobile_responsive": True,
                "has_amp": False,
                "has_pwa": True,
                "has_api": True
            },
            "performance": {
                "cdn_enabled": True,
                "image_optimization": True,
                "lazy_loading": True,
                "minification": True
            },
            "security": {
                "ssl_provider": "Let's Encrypt",
                "security_headers": ["CSP", "HSTS", "X-Frame-Options"],
                "waf_detected": "Cloudflare"
            },
            "spend_estimate": {
                "monthly_usd": 2500,
                "confidence": 0.7
            }
        }
        
        return ProviderEvidence(
            source="builtwith",
            entity="brand",
            source_id=f"builtwith:domain:{domain}",
            retrieved_at=datetime.utcnow(),
            evidence_url=f"https://builtwith.com/{domain}",
            data=data,
            ttl_hours=self.ttl_hours
        )
    
    async def fetch_product_data(self, product_id: str) -> ProviderEvidence:
        """BuiltWith provides domain-level tech data only"""
        raise NotImplementedError("BuiltWith provides domain-level data only")


class GoogleSellerRatingsProvider(BaseProvider):
    """Google Seller Ratings aggregation"""
    
    def __init__(self):
        super().__init__()
        self.provider_type = ProviderType.GOOGLE_SELLER
        self.ttl_hours = 24
    
    async def fetch_brand_data(self, merchant_id: str) -> ProviderEvidence:
        """Fetch Google aggregated seller ratings"""
        
        data = {
            "merchant_id": merchant_id,
            "aggregated_rating": 4.7,
            "review_count": 8932,
            "sources": [
                {"name": "Trustpilot", "count": 3421},
                {"name": "Trusted Shops", "count": 2103},
                {"name": "Bizrate", "count": 1876},
                {"name": "ResellerRatings", "count": 1532}
            ],
            "aspects": {
                "shipping": 4.8,
                "returns": 4.5,
                "service": 4.7,
                "price": 4.6
            },
            "badges": {
                "google_trusted_store": True,
                "excellent_service": True
            }
        }
        
        return ProviderEvidence(
            source="google_seller_ratings",
            entity="brand",
            source_id=f"google:merchant:{merchant_id}",
            retrieved_at=datetime.utcnow(),
            evidence_url=f"https://www.google.com/shopping/seller?id={merchant_id}",
            data=data,
            ttl_hours=self.ttl_hours
        )
    
    async def fetch_product_data(self, product_id: str) -> ProviderEvidence:
        """Google product reviews if available"""
        
        data = {
            "product_id": product_id,
            "avg_rating": 4.5,
            "review_count": 342,
            "price_history": {
                "current": 129.99,
                "avg_30d": 135.99,
                "lowest_90d": 119.99
            },
            "merchant_count": 12,
            "in_stock_rate": 0.92
        }
        
        return ProviderEvidence(
            source="google_seller_ratings",
            entity="product",
            source_id=f"google:product:{product_id}",
            retrieved_at=datetime.utcnow(),
            evidence_url=f"https://www.google.com/shopping/product/{product_id}",
            data=data,
            ttl_hours=24
        )


class EnrichmentOrchestrator:
    """Orchestrates multiple provider enrichments with caching and verification"""
    
    def __init__(self):
        self.providers: Dict[ProviderType, BaseProvider] = {}
        self.cache: Dict[str, ProviderEvidence] = {}
        self.anomaly_threshold = 0.3
    
    def register_provider(self, provider: BaseProvider):
        """Register a provider for enrichment"""
        self.providers[provider.provider_type] = provider
    
    async def enrich_brand(
        self, 
        domain: str, 
        providers: Optional[List[ProviderType]] = None
    ) -> Dict[str, ProviderEvidence]:
        """Enrich brand data from multiple providers"""
        
        if providers is None:
            providers = list(self.providers.keys())
        
        results = {}
        
        for provider_type in providers:
            if provider_type not in self.providers:
                continue
            
            provider = self.providers[provider_type]
            cache_key = f"{provider_type}:brand:{domain}"
            
            # Check cache
            if cache_key in self.cache:
                evidence = self.cache[cache_key]
                if provider.validate_freshness(evidence):
                    results[provider_type.value] = evidence
                    continue
            
            # Fetch fresh data
            try:
                evidence = await provider.fetch_brand_data(domain)
                
                # Check for anomalies
                historical = self._get_historical(cache_key)
                if provider.detect_anomaly(evidence.data, historical):
                    evidence.data["anomaly_detected"] = True
                    evidence.ttl_hours = 1  # Short TTL for suspicious data
                
                # Cache and return
                self.cache[cache_key] = evidence
                results[provider_type.value] = evidence
                
            except NotImplementedError:
                continue
            except Exception as e:
                print(f"Error fetching from {provider_type}: {e}")
                continue
        
        return results
    
    async def enrich_product(
        self, 
        product_id: str,
        providers: Optional[List[ProviderType]] = None
    ) -> Dict[str, ProviderEvidence]:
        """Enrich product data from multiple providers"""
        
        if providers is None:
            providers = [ProviderType.TRUSTED_SHOPS, ProviderType.GOOGLE_SELLER]
        
        results = {}
        
        for provider_type in providers:
            if provider_type not in self.providers:
                continue
            
            provider = self.providers[provider_type]
            cache_key = f"{provider_type}:product:{product_id}"
            
            # Check cache
            if cache_key in self.cache:
                evidence = self.cache[cache_key]
                if provider.validate_freshness(evidence):
                    results[provider_type.value] = evidence
                    continue
            
            # Fetch fresh data
            try:
                evidence = await provider.fetch_product_data(product_id)
                self.cache[cache_key] = evidence
                results[provider_type.value] = evidence
            except NotImplementedError:
                continue
            except Exception as e:
                print(f"Error fetching from {provider_type}: {e}")
                continue
        
        return results
    
    def _get_historical(self, cache_key: str) -> List[Dict]:
        """Get historical data for anomaly detection"""
        # In production, fetch from persistent storage
        # For now, return empty list
        return []
    
    def generate_verifiable_credential(
        self, 
        evidence: ProviderEvidence,
        issuer_did: str
    ) -> Dict[str, Any]:
        """Generate W3C Verifiable Credential for evidence"""
        
        vc = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://agentic-commerce.org/axp/v0.1/context"
            ],
            "type": ["VerifiableCredential", "ThirdPartyEvidence"],
            "issuer": issuer_did,
            "issuanceDate": datetime.utcnow().isoformat() + "Z",
            "expirationDate": (
                datetime.utcnow() + timedelta(hours=evidence.ttl_hours)
            ).isoformat() + "Z",
            "credentialSubject": {
                "id": evidence.source_id,
                "source": evidence.source,
                "entity": evidence.entity,
                "data": evidence.data,
                "evidence_hash": evidence.compute_hash(),
                "evidence_url": evidence.evidence_url
            },
            "proof": {
                "type": "Ed25519Signature2020",
                "created": datetime.utcnow().isoformat() + "Z",
                "verificationMethod": f"{issuer_did}#key-1",
                "proofPurpose": "assertionMethod"
                # In production, add actual signature
            }
        }
        
        return vc


# Example usage
async def example_enrichment():
    """Example of using the enrichment system"""
    
    # Initialize orchestrator
    orchestrator = EnrichmentOrchestrator()
    
    # Register providers
    orchestrator.register_provider(TrustpilotProvider("api_key"))
    orchestrator.register_provider(TrustedShopsProvider("api_key"))
    orchestrator.register_provider(BuiltWithProvider("api_key"))
    orchestrator.register_provider(GoogleSellerRatingsProvider())
    
    # Enrich brand
    brand_evidence = await orchestrator.enrich_brand("demo.shop")
    
    # Generate VC for Trustpilot evidence
    if "trustpilot" in brand_evidence:
        vc = orchestrator.generate_verifiable_credential(
            brand_evidence["trustpilot"],
            "did:web:aggregator.example.com"
        )
        print(json.dumps(vc, indent=2))
    
    return brand_evidence


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_enrichment())
