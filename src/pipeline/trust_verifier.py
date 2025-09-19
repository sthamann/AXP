"""
AXP Trust Signal Verifier
Verification and validation of external trust signals with anti-gaming measures
"""

import hashlib
import json
import time
import requests
import dns.resolver
import whois
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import statistics
import math
from urllib.parse import urlparse


class VerificationMethod(Enum):
    API = "api"
    SNAPSHOT = "snapshot"
    ATTESTED = "attested"
    VC = "verifiable_credential"
    WEBHOOK = "webhook"
    SIGNED_FILE = "signed_file"


@dataclass
class VerificationResult:
    """Result of trust signal verification"""
    method: VerificationMethod
    confidence: float
    last_checked: datetime
    source_signature: Optional[str]
    snapshot_hash: Optional[str]
    anomalies: List[str]
    raw_data: Optional[Dict]


@dataclass
class DomainAgeResult:
    """Domain age analysis result"""
    domain: str
    earliest_date: datetime
    age_days: int
    age_score: float
    confidence: float
    sources: List[str]


class TrustVerifier:
    """Verify and validate trust signals from external sources"""
    
    def __init__(self):
        self.trusted_apis = {
            'trustpilot': 'https://api.trustpilot.com/v1/',
            'google': 'https://maps.googleapis.com/maps/api/',
            'tripadvisor': 'https://api.tripadvisor.com/',
            'bbb': 'https://api.bbb.org/',
            'capterra': 'https://api.capterra.com/'
        }
        
        self.certification_validators = {
            'iso': self._validate_iso_cert,
            'organic': self._validate_organic_cert,
            'fairtrade': self._validate_fairtrade_cert,
            'bcorp': self._validate_bcorp_cert
        }
        
    def verify_review_source(self, 
                            source: str, 
                            business_id: str,
                            expected_stats: Dict) -> VerificationResult:
        """
        Verify review statistics from external source
        
        Args:
            source: Review platform name
            business_id: Business identifier on platform
            expected_stats: Expected statistics to verify
            
        Returns:
            VerificationResult with confidence and anomalies
        """
        
        anomalies = []
        
        # Try API verification first
        if source.lower() in self.trusted_apis:
            try:
                api_data = self._fetch_via_api(source, business_id)
                
                # Compare with expected
                anomalies.extend(self._detect_review_anomalies(api_data, expected_stats))
                
                # Generate signature
                signature = self._generate_api_signature(api_data)
                
                return VerificationResult(
                    method=VerificationMethod.API,
                    confidence=0.95 if len(anomalies) == 0 else 0.7,
                    last_checked=datetime.now(),
                    source_signature=signature,
                    snapshot_hash=None,
                    anomalies=anomalies,
                    raw_data=api_data
                )
                
            except Exception as e:
                anomalies.append(f"API verification failed: {str(e)}")
        
        # Fallback to snapshot verification
        snapshot_data = self._fetch_snapshot(source, business_id)
        snapshot_hash = self._hash_snapshot(snapshot_data)
        
        # Check for anomalies
        anomalies.extend(self._detect_review_anomalies(snapshot_data, expected_stats))
        
        # Time series analysis
        if 'history' in snapshot_data:
            anomalies.extend(self._detect_time_anomalies(snapshot_data['history']))
        
        # Distribution analysis
        if 'rating_distribution' in snapshot_data:
            anomalies.extend(self._detect_distribution_anomalies(
                snapshot_data['rating_distribution']
            ))
        
        confidence = self._calculate_confidence(anomalies, snapshot_data)
        
        return VerificationResult(
            method=VerificationMethod.SNAPSHOT,
            confidence=confidence,
            last_checked=datetime.now(),
            source_signature=None,
            snapshot_hash=snapshot_hash,
            anomalies=anomalies,
            raw_data=snapshot_data
        )
    
    def verify_certification(self, 
                           cert_type: str,
                           cert_id: str,
                           issuer: str) -> VerificationResult:
        """Verify certification validity"""
        
        anomalies = []
        
        # Check if we have a validator for this cert type
        if cert_type.lower() in self.certification_validators:
            validator = self.certification_validators[cert_type.lower()]
            is_valid, details = validator(cert_id, issuer)
            
            if not is_valid:
                anomalies.append(f"Certification validation failed: {details}")
            
            return VerificationResult(
                method=VerificationMethod.API,
                confidence=0.95 if is_valid else 0.2,
                last_checked=datetime.now(),
                source_signature=details.get('signature'),
                snapshot_hash=None,
                anomalies=anomalies,
                raw_data=details
            )
        
        # Generic verification via snapshot
        cert_data = self._fetch_certification_data(cert_type, cert_id, issuer)
        
        # Check expiry
        if 'expiry_date' in cert_data:
            expiry = datetime.fromisoformat(cert_data['expiry_date'])
            if expiry < datetime.now():
                anomalies.append("Certification expired")
        
        # Check revocation
        if self._check_revocation(cert_type, cert_id):
            anomalies.append("Certification revoked")
        
        return VerificationResult(
            method=VerificationMethod.SNAPSHOT,
            confidence=0.7 if len(anomalies) == 0 else 0.3,
            last_checked=datetime.now(),
            source_signature=None,
            snapshot_hash=self._hash_snapshot(cert_data),
            anomalies=anomalies,
            raw_data=cert_data
        )
    
    def verify_verifiable_credential(self, vc_data: Dict) -> VerificationResult:
        """Verify a W3C Verifiable Credential"""
        
        anomalies = []
        
        # Check structure
        required_fields = ['@context', 'type', 'issuer', 'issuanceDate', 'credentialSubject', 'proof']
        for field in required_fields:
            if field not in vc_data:
                anomalies.append(f"Missing required field: {field}")
        
        if anomalies:
            return VerificationResult(
                method=VerificationMethod.VC,
                confidence=0.1,
                last_checked=datetime.now(),
                source_signature=None,
                snapshot_hash=None,
                anomalies=anomalies,
                raw_data=vc_data
            )
        
        # Verify proof
        proof_valid = self._verify_vc_proof(vc_data)
        if not proof_valid:
            anomalies.append("Proof verification failed")
        
        # Check expiration
        if 'expirationDate' in vc_data:
            expiry = datetime.fromisoformat(vc_data['expirationDate'].replace('Z', '+00:00'))
            if expiry < datetime.now():
                anomalies.append("Credential expired")
        
        # Check revocation status
        if 'credentialStatus' in vc_data:
            if self._check_vc_revocation(vc_data['credentialStatus']):
                anomalies.append("Credential revoked")
        
        # Verify issuer
        issuer_trusted = self._verify_issuer(vc_data['issuer'])
        if not issuer_trusted:
            anomalies.append("Issuer not in trust registry")
        
        confidence = 0.95 if len(anomalies) == 0 else max(0.2, 0.95 - len(anomalies) * 0.2)
        
        return VerificationResult(
            method=VerificationMethod.VC,
            confidence=confidence,
            last_checked=datetime.now(),
            source_signature=vc_data.get('proof', {}).get('jws'),
            snapshot_hash=None,
            anomalies=anomalies,
            raw_data=vc_data
        )
    
    def calculate_domain_age(self, domain: str) -> DomainAgeResult:
        """
        Calculate domain age from multiple sources
        
        Uses:
        - WHOIS creation date
        - First SSL certificate
        - DNS history
        - Internet Archive
        """
        
        earliest_date = None
        sources = []
        
        # 1. WHOIS lookup
        try:
            w = whois.whois(domain)
            if w.creation_date:
                creation = w.creation_date
                if isinstance(creation, list):
                    creation = creation[0]
                if creation:
                    earliest_date = creation
                    sources.append('whois')
        except Exception:
            pass
        
        # 2. Certificate Transparency logs
        try:
            ct_date = self._get_earliest_cert(domain)
            if ct_date and (not earliest_date or ct_date < earliest_date):
                earliest_date = ct_date
                sources.append('certificate_transparency')
        except Exception:
            pass
        
        # 3. DNS history
        try:
            dns_date = self._get_dns_first_seen(domain)
            if dns_date and (not earliest_date or dns_date < earliest_date):
                earliest_date = dns_date
                sources.append('dns_history')
        except Exception:
            pass
        
        # 4. Internet Archive
        try:
            archive_date = self._get_archive_first_seen(domain)
            if archive_date and (not earliest_date or archive_date < earliest_date):
                earliest_date = archive_date
                sources.append('internet_archive')
        except Exception:
            pass
        
        # Calculate age and score
        if earliest_date:
            age_days = (datetime.now() - earliest_date).days
            
            # Saturating function with cap
            k = 365  # Half-life of 1 year
            raw_score = 1 - math.exp(-age_days / k)
            age_score = min(raw_score, 0.6)  # Cap at 0.6
            
            confidence = min(1.0, len(sources) / 2)  # Higher confidence with more sources
            
        else:
            # No data found
            age_days = 0
            age_score = 0.0
            confidence = 0.0
        
        return DomainAgeResult(
            domain=domain,
            earliest_date=earliest_date or datetime.now(),
            age_days=age_days,
            age_score=age_score,
            confidence=confidence,
            sources=sources
        )
    
    def _detect_review_anomalies(self, actual: Dict, expected: Dict) -> List[str]:
        """Detect anomalies in review data"""
        anomalies = []
        
        # Check rating jump
        if 'avg_rating' in both(actual, expected):
            diff = abs(actual['avg_rating'] - expected['avg_rating'])
            if diff > 0.5:
                anomalies.append(f"Rating discrepancy: {diff:.1f}")
        
        # Check review count jump
        if 'total_reviews' in both(actual, expected):
            actual_count = actual['total_reviews']
            expected_count = expected['total_reviews']
            if actual_count > expected_count * 1.5:
                anomalies.append(f"Suspicious review count increase: {actual_count - expected_count}")
        
        # Check verified ratio
        if 'verified_ratio' in actual:
            if actual['verified_ratio'] < 0.3:
                anomalies.append(f"Low verified review ratio: {actual['verified_ratio']:.1%}")
        
        return anomalies
    
    def _detect_time_anomalies(self, history: List[Dict]) -> List[str]:
        """Detect temporal anomalies in review history"""
        anomalies = []
        
        if len(history) < 3:
            return anomalies
        
        # Extract daily counts
        daily_counts = [h['count'] for h in history]
        
        # Check for spikes
        mean = statistics.mean(daily_counts)
        std = statistics.stdev(daily_counts) if len(daily_counts) > 1 else 0
        
        for i, count in enumerate(daily_counts):
            if std > 0 and count > mean + 3 * std:
                anomalies.append(f"Review spike on day {i}: {count} reviews (mean: {mean:.1f})")
        
        # Check for clustering
        cluster_threshold = mean * 3
        cluster_days = 0
        for count in daily_counts:
            if count > cluster_threshold:
                cluster_days += 1
        
        if cluster_days > len(daily_counts) * 0.1:
            anomalies.append(f"Review clustering detected: {cluster_days} high-activity days")
        
        return anomalies
    
    def _detect_distribution_anomalies(self, distribution: Dict) -> List[str]:
        """Detect anomalies in rating distribution"""
        anomalies = []
        
        # Expected J-shaped or normal distribution
        ratings = [int(k) for k in distribution.keys()]
        counts = [distribution[str(r)] for r in ratings]
        total = sum(counts)
        
        if total == 0:
            return anomalies
        
        # Check for unnatural uniformity
        proportions = [c/total for c in counts]
        uniformity = statistics.stdev(proportions) if len(proportions) > 1 else 0
        
        if uniformity < 0.05:  # Too uniform
            anomalies.append("Unnaturally uniform rating distribution")
        
        # Check for missing middle (bimodal)
        if counts[2] < counts[0] * 0.5 and counts[2] < counts[4] * 0.5:
            anomalies.append("Bimodal distribution suggests manipulation")
        
        # Check 5-star dominance
        if counts[4] > total * 0.7:
            anomalies.append(f"Excessive 5-star ratings: {counts[4]/total:.1%}")
        
        return anomalies
    
    def _calculate_confidence(self, anomalies: List[str], data: Dict) -> float:
        """Calculate confidence score based on anomalies and data quality"""
        
        base_confidence = 0.8
        
        # Reduce for each anomaly
        confidence = base_confidence * (0.9 ** len(anomalies))
        
        # Boost for verified reviews
        if 'verified_ratio' in data:
            confidence *= (0.7 + 0.3 * data['verified_ratio'])
        
        # Boost for large sample size
        if 'total_reviews' in data:
            sample_factor = min(1.0, math.log(data['total_reviews'] + 1) / math.log(1000))
            confidence *= (0.8 + 0.2 * sample_factor)
        
        return min(1.0, max(0.1, confidence))
    
    def _fetch_via_api(self, source: str, business_id: str) -> Dict:
        """Fetch data via official API"""
        # Mock implementation
        return {
            'avg_rating': 4.5,
            'total_reviews': 1234,
            'verified_ratio': 0.85,
            'last_updated': datetime.now().isoformat()
        }
    
    def _fetch_snapshot(self, source: str, business_id: str) -> Dict:
        """Fetch snapshot of public data"""
        # Mock implementation
        return {
            'avg_rating': 4.5,
            'total_reviews': 1234,
            'verified_ratio': 0.85,
            'rating_distribution': {'1': 10, '2': 20, '3': 50, '4': 300, '5': 854},
            'snapshot_timestamp': datetime.now().isoformat()
        }
    
    def _hash_snapshot(self, data: Dict) -> str:
        """Generate SHA-256 hash of snapshot data"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _generate_api_signature(self, data: Dict) -> str:
        """Generate signature for API response"""
        # In production, use HMAC with API secret
        return hashlib.sha256(json.dumps(data).encode()).hexdigest()[:16]
    
    def _validate_iso_cert(self, cert_id: str, issuer: str) -> Tuple[bool, Dict]:
        """Validate ISO certification"""
        # Mock implementation - in production, check with ISO database
        return True, {'signature': 'iso_sig_123', 'valid_until': '2026-01-01'}
    
    def _validate_organic_cert(self, cert_id: str, issuer: str) -> Tuple[bool, Dict]:
        """Validate organic certification"""
        return True, {'signature': 'organic_sig_456', 'valid_until': '2025-12-31'}
    
    def _validate_fairtrade_cert(self, cert_id: str, issuer: str) -> Tuple[bool, Dict]:
        """Validate Fairtrade certification"""
        return True, {'signature': 'ft_sig_789', 'valid_until': '2025-06-30'}
    
    def _validate_bcorp_cert(self, cert_id: str, issuer: str) -> Tuple[bool, Dict]:
        """Validate B-Corp certification"""
        return True, {'signature': 'bcorp_sig_012', 'score': 85.5}
    
    def _fetch_certification_data(self, cert_type: str, cert_id: str, issuer: str) -> Dict:
        """Fetch certification data"""
        return {
            'cert_type': cert_type,
            'cert_id': cert_id,
            'issuer': issuer,
            'expiry_date': '2026-01-01T00:00:00Z',
            'status': 'active'
        }
    
    def _check_revocation(self, cert_type: str, cert_id: str) -> bool:
        """Check if certification is revoked"""
        # Mock - in production check revocation lists
        return False
    
    def _verify_vc_proof(self, vc_data: Dict) -> bool:
        """Verify cryptographic proof of VC"""
        # Mock - in production verify JWS/LD-proof
        return 'proof' in vc_data
    
    def _check_vc_revocation(self, status: Dict) -> bool:
        """Check VC revocation status"""
        # Mock - in production check status endpoint
        return False
    
    def _verify_issuer(self, issuer: str) -> bool:
        """Verify issuer is in trust registry"""
        trusted_issuers = [
            'did:web:example.com',
            'did:key:z6MkhaXgBZD',
            'https://issuer.example.com'
        ]
        return issuer in trusted_issuers
    
    def _get_earliest_cert(self, domain: str) -> Optional[datetime]:
        """Get earliest certificate from CT logs"""
        # Mock - in production query crt.sh or similar
        return datetime(2020, 1, 1)
    
    def _get_dns_first_seen(self, domain: str) -> Optional[datetime]:
        """Get first DNS record"""
        # Mock - in production use SecurityTrails or similar
        return datetime(2019, 6, 1)
    
    def _get_archive_first_seen(self, domain: str) -> Optional[datetime]:
        """Get first Internet Archive snapshot"""
        # Mock - in production query Wayback Machine API
        return datetime(2019, 3, 15)


def both(dict1: Dict, dict2: Dict) -> bool:
    """Helper to check if key exists in both dicts"""
    return all(k in d for k in dict1.keys() & dict2.keys() for d in [dict1, dict2])


# Example usage
def example_verification():
    verifier = TrustVerifier()
    
    # Verify reviews
    review_result = verifier.verify_review_source(
        source='trustpilot',
        business_id='example-store',
        expected_stats={'avg_rating': 4.5, 'total_reviews': 1200}
    )
    print(f"Review verification: {review_result.confidence:.2f}")
    print(f"Anomalies: {review_result.anomalies}")
    
    # Verify certification
    cert_result = verifier.verify_certification(
        cert_type='iso',
        cert_id='ISO9001:2015',
        issuer='SGS'
    )
    print(f"Certification valid: {cert_result.confidence:.2f}")
    
    # Check domain age
    domain_result = verifier.calculate_domain_age('example.com')
    print(f"Domain age: {domain_result.age_days} days (score: {domain_result.age_score:.2f})")
    
    # Verify VC
    vc = {
        '@context': ['https://www.w3.org/2018/credentials/v1'],
        'type': ['VerifiableCredential', 'ProductCertification'],
        'issuer': 'did:web:example.com',
        'issuanceDate': '2025-01-01T00:00:00Z',
        'credentialSubject': {
            'id': 'sku_123',
            'certification': 'Organic'
        },
        'proof': {
            'type': 'JsonWebSignature2020',
            'jws': 'eyJhbGc...'
        }
    }
    vc_result = verifier.verify_verifiable_credential(vc)
    print(f"VC verification: {vc_result.confidence:.2f}")


if __name__ == '__main__':
    example_verification()
