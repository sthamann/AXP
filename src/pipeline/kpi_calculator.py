"""
AXP Soft KPI Calculator
Precise calculation of soft signals from measurable sub-factors
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import statistics


@dataclass
class KPIEvidence:
    """Evidence for a KPI calculation"""
    factor: str
    value: float
    source: str
    confidence: float
    timestamp: datetime


@dataclass
class SoftSignals:
    """Complete soft signals with evidence"""
    fit_hint_score: float
    reliability_score: float
    performance_score: float
    owner_satisfaction_score: float
    uniqueness_score: float
    craftsmanship_score: float
    sustainability_score: float
    innovation_score: float
    evidence: List[KPIEvidence]
    calculation_method: str
    last_updated: datetime


class KPICalculator:
    """Calculate all soft KPIs with proper normalization and evidence tracking"""
    
    def __init__(self):
        # Weights for different factors (calibrated from data)
        self.weights = {
            'fit_hint': {
                'return_size': -0.4,  # negative correlation
                'exchange_size': -0.2,
                'advisor_usage': 0.2,
                'aspect_fit_positive': 0.2
            },
            'reliability': {
                'rma_rate': -0.3,
                'claim_rate': -0.3,
                'mtbf': 0.2,
                'warranty_claims': -0.1,
                'aspect_durability': 0.1
            },
            'performance': {
                'benchmark_scores': 0.4,
                'energy_return': 0.2,
                'weight_factor': 0.1,
                'lab_tests': 0.3
            },
            'owner_satisfaction': {
                'rating_verified': 0.4,
                'csat_product': 0.3,
                'recent_sentiment': 0.2,
                'repeat_purchase': 0.1
            }
        }
        
    def calculate_fit_hint_score(self, product_data: Dict) -> Tuple[float, List[KPIEvidence]]:
        """
        Calculate fit hint score from return and sizing data
        
        Factors:
        - Return rate due to size (inverse)
        - Exchange to different size rate
        - Size advisor usage before purchase
        - Positive fit mentions in reviews
        """
        evidence = []
        
        # Extract factors
        returns_total = product_data.get('returns_total', 0)
        returns_size = product_data.get('returns_size', 0)
        exchanges_size = product_data.get('exchanges_size', 0)
        purchases_with_advisor = product_data.get('purchases_with_advisor', 0)
        purchases_total = max(product_data.get('purchases_total', 1), 1)
        reviews_fit_positive = product_data.get('reviews_fit_positive', 0)
        reviews_with_fit = max(product_data.get('reviews_with_fit', 1), 1)
        
        # Calculate rates
        return_size_rate = returns_size / max(returns_total, 1)
        exchange_size_rate = exchanges_size / purchases_total
        advisor_usage_rate = purchases_with_advisor / purchases_total
        fit_positive_rate = reviews_fit_positive / reviews_with_fit
        
        # Store evidence
        evidence.append(KPIEvidence(
            factor='return_size_rate',
            value=return_size_rate,
            source='returns_data',
            confidence=min(1.0, returns_total / 10),  # Confidence grows with sample size
            timestamp=datetime.now()
        ))
        
        evidence.append(KPIEvidence(
            factor='advisor_usage_rate',
            value=advisor_usage_rate,
            source='purchase_behavior',
            confidence=min(1.0, purchases_total / 50),
            timestamp=datetime.now()
        ))
        
        evidence.append(KPIEvidence(
            factor='fit_positive_rate',
            value=fit_positive_rate,
            source='review_analysis',
            confidence=min(1.0, reviews_with_fit / 20),
            timestamp=datetime.now()
        ))
        
        # Calculate weighted score
        raw_score = (
            self.weights['fit_hint']['return_size'] * return_size_rate +
            self.weights['fit_hint']['exchange_size'] * exchange_size_rate +
            self.weights['fit_hint']['advisor_usage'] * advisor_usage_rate +
            self.weights['fit_hint']['aspect_fit_positive'] * fit_positive_rate
        )
        
        # Normalize with sigmoid
        score = self._sigmoid(raw_score + 0.5)  # Shift to center around 0.5
        
        return score, evidence
    
    def calculate_reliability_score(self, product_data: Dict) -> Tuple[float, List[KPIEvidence]]:
        """
        Calculate reliability score from defect and warranty data
        
        Factors:
        - RMA (Return Merchandise Authorization) rate
        - Claim rate
        - Mean time between failures (MTBF)
        - Warranty claim rate
        - Durability aspect in reviews
        """
        evidence = []
        
        # Extract factors
        rma_count = product_data.get('rma_count', 0)
        claim_count = product_data.get('claim_count', 0)
        units_sold = max(product_data.get('units_sold', 1000), 1)
        avg_days_to_claim = product_data.get('avg_days_to_claim', 365)
        warranty_claims = product_data.get('warranty_claims', 0)
        reviews_durability_avg = product_data.get('reviews_durability_avg', 0.5)
        
        # Calculate rates (per 1000 units)
        rma_rate = (rma_count / units_sold) * 1000
        claim_rate = (claim_count / units_sold) * 1000
        warranty_rate = (warranty_claims / units_sold) * 1000
        
        # MTBF proxy from average days to claim
        mtbf_normalized = min(1.0, avg_days_to_claim / 730)  # Normalize to 2 years
        
        # Store evidence
        evidence.append(KPIEvidence(
            factor='rma_per_1000',
            value=rma_rate,
            source='warranty_system',
            confidence=min(1.0, units_sold / 1000),
            timestamp=datetime.now()
        ))
        
        evidence.append(KPIEvidence(
            factor='mtbf_days',
            value=avg_days_to_claim,
            source='warranty_system',
            confidence=min(1.0, claim_count / 10) if claim_count > 0 else 0.1,
            timestamp=datetime.now()
        ))
        
        # Category normalization (compare to category average)
        category_rma_avg = product_data.get('category_rma_avg', 5.0)
        rma_rate_normalized = 1.0 - min(1.0, rma_rate / category_rma_avg)
        claim_rate_normalized = 1.0 - min(1.0, claim_rate / (category_rma_avg * 2))
        
        # Calculate weighted score
        raw_score = (
            self.weights['reliability']['rma_rate'] * rma_rate_normalized +
            self.weights['reliability']['claim_rate'] * claim_rate_normalized +
            self.weights['reliability']['mtbf'] * mtbf_normalized +
            self.weights['reliability']['warranty_claims'] * (1 - min(1.0, warranty_rate / 10)) +
            self.weights['reliability']['aspect_durability'] * reviews_durability_avg
        )
        
        score = self._sigmoid(raw_score)
        
        return score, evidence
    
    def calculate_performance_score(self, product_data: Dict, category: str) -> Tuple[float, List[KPIEvidence]]:
        """
        Calculate domain-specific performance score
        
        Factors vary by category:
        - Footwear: energy return, weight, cushioning
        - Electronics: benchmarks, efficiency, latency
        - Apparel: color fastness, fabric weight, abrasion
        """
        evidence = []
        
        if category == 'footwear':
            # Footwear-specific metrics
            energy_return = product_data.get('energy_return_percent', 50) / 100
            weight_grams = product_data.get('weight_grams', 300)
            cushioning_index = product_data.get('cushioning_index', 5) / 10
            stack_height = product_data.get('stack_height_mm', 25)
            
            # Normalize weight (lighter is better, up to a point)
            weight_score = 1.0 - min(1.0, max(0, weight_grams - 200) / 300)
            
            # Stack height preference depends on use case
            stack_score = min(1.0, stack_height / 40) if category == 'running' else 0.5
            
            evidence.append(KPIEvidence(
                factor='energy_return',
                value=energy_return,
                source='lab_test',
                confidence=0.95,
                timestamp=datetime.now()
            ))
            
            evidence.append(KPIEvidence(
                factor='weight_score',
                value=weight_score,
                source='product_specs',
                confidence=1.0,
                timestamp=datetime.now()
            ))
            
            raw_score = (
                0.4 * energy_return +
                0.2 * weight_score +
                0.2 * cushioning_index +
                0.2 * stack_score
            )
            
        elif category == 'electronics':
            # Electronics-specific metrics
            benchmark_score = product_data.get('benchmark_percentile', 50) / 100
            efficiency_rating = product_data.get('efficiency_rating', 3) / 5
            latency_ms = product_data.get('latency_ms', 100)
            
            latency_score = 1.0 - min(1.0, latency_ms / 200)
            
            evidence.append(KPIEvidence(
                factor='benchmark_percentile',
                value=benchmark_score,
                source='benchmark_suite',
                confidence=0.9,
                timestamp=datetime.now()
            ))
            
            raw_score = (
                0.5 * benchmark_score +
                0.3 * efficiency_rating +
                0.2 * latency_score
            )
            
        else:
            # Generic performance based on reviews
            performance_mentions = product_data.get('reviews_performance_avg', 0.5)
            category_avg = product_data.get('category_performance_avg', 0.5)
            
            raw_score = performance_mentions / max(category_avg, 0.1)
            
        # Normalize against category
        score = min(1.0, self._sigmoid(raw_score))
        
        return score, evidence
    
    def calculate_owner_satisfaction_score(self, product_data: Dict) -> Tuple[float, List[KPIEvidence]]:
        """
        Calculate owner satisfaction from multiple sources
        
        Factors:
        - Verified review ratings (higher weight)
        - Product-specific CSAT scores
        - Recent sentiment trend
        - Repeat purchase rate
        """
        evidence = []
        
        # Review data
        avg_rating_all = product_data.get('avg_rating', 3.0)
        avg_rating_verified = product_data.get('avg_rating_verified', avg_rating_all)
        review_count_verified = product_data.get('review_count_verified', 0)
        review_count_total = max(product_data.get('review_count_total', 1), 1)
        
        # CSAT data
        csat_score = product_data.get('csat_product', 0.7)
        csat_responses = product_data.get('csat_responses', 0)
        
        # Sentiment trend (last 90 days vs previous)
        sentiment_recent = product_data.get('sentiment_90d', 0.5)
        sentiment_previous = product_data.get('sentiment_prev_90d', 0.5)
        sentiment_trend = sentiment_recent - sentiment_previous
        
        # Repeat purchase
        repeat_purchase_rate = product_data.get('repeat_purchase_rate', 0.1)
        
        # Calculate verification ratio
        verification_ratio = review_count_verified / review_count_total
        
        # Weighted rating (verified reviews count more)
        weighted_rating = (
            (avg_rating_verified * review_count_verified * 1.5 + 
             avg_rating_all * (review_count_total - review_count_verified)) /
            (review_count_verified * 1.5 + (review_count_total - review_count_verified))
        )
        
        # Normalize rating to 0-1
        rating_normalized = (weighted_rating - 1) / 4  # 1-5 scale to 0-1
        
        evidence.append(KPIEvidence(
            factor='weighted_rating',
            value=weighted_rating,
            source='review_system',
            confidence=min(1.0, review_count_total / 100),
            timestamp=datetime.now()
        ))
        
        evidence.append(KPIEvidence(
            factor='csat_score',
            value=csat_score,
            source='survey_system',
            confidence=min(1.0, csat_responses / 50),
            timestamp=datetime.now()
        ))
        
        evidence.append(KPIEvidence(
            factor='sentiment_trend',
            value=sentiment_trend,
            source='sentiment_analysis',
            confidence=0.8,
            timestamp=datetime.now()
        ))
        
        # Calculate weighted score
        raw_score = (
            self.weights['owner_satisfaction']['rating_verified'] * rating_normalized +
            self.weights['owner_satisfaction']['csat_product'] * csat_score +
            self.weights['owner_satisfaction']['recent_sentiment'] * (sentiment_recent + sentiment_trend) +
            self.weights['owner_satisfaction']['repeat_purchase'] * repeat_purchase_rate
        )
        
        score = min(1.0, self._sigmoid(raw_score))
        
        return score, evidence
    
    def calculate_uniqueness_score(self, product_data: Dict) -> Tuple[float, List[KPIEvidence]]:
        """Calculate uniqueness relative to market"""
        evidence = []
        
        # Feature rarity
        rare_features = product_data.get('rare_feature_count', 0)
        total_features = max(product_data.get('total_feature_count', 10), 1)
        feature_rarity = rare_features / total_features
        
        # Limited edition / exclusive
        is_limited = product_data.get('is_limited_edition', False)
        stock_scarcity = product_data.get('stock_scarcity_score', 0.0)
        
        # Price positioning
        price_percentile = product_data.get('price_percentile_category', 50) / 100
        
        evidence.append(KPIEvidence(
            factor='feature_rarity',
            value=feature_rarity,
            source='market_analysis',
            confidence=0.7,
            timestamp=datetime.now()
        ))
        
        score = self._sigmoid(
            feature_rarity * 0.4 +
            (1.0 if is_limited else 0.0) * 0.2 +
            stock_scarcity * 0.2 +
            price_percentile * 0.2
        )
        
        return score, evidence
    
    def calculate_craftsmanship_score(self, product_data: Dict) -> Tuple[float, List[KPIEvidence]]:
        """Calculate craftsmanship from materials and reviews"""
        evidence = []
        
        # Material quality indicators
        material_grade = product_data.get('material_grade', 'standard')
        material_scores = {'premium': 0.9, 'high': 0.7, 'standard': 0.5, 'basic': 0.3}
        material_score = material_scores.get(material_grade, 0.5)
        
        # Manufacturing origin
        origin_score = product_data.get('origin_reputation_score', 0.5)
        
        # Warranty as quality signal
        warranty_days = product_data.get('warranty_days', 90)
        warranty_score = min(1.0, warranty_days / 730)  # 2 years = 1.0
        
        # Review aspects
        review_quality_aspect = product_data.get('review_aspect_quality', 0.5)
        review_craftsmanship_mentions = product_data.get('craftsmanship_mention_rate', 0.0)
        
        evidence.append(KPIEvidence(
            factor='material_grade',
            value=material_score,
            source='product_specs',
            confidence=0.9,
            timestamp=datetime.now()
        ))
        
        score = self._sigmoid(
            material_score * 0.3 +
            origin_score * 0.2 +
            warranty_score * 0.2 +
            review_quality_aspect * 0.2 +
            review_craftsmanship_mentions * 0.1
        )
        
        return score, evidence
    
    def calculate_sustainability_score(self, product_data: Dict) -> Tuple[float, List[KPIEvidence]]:
        """Calculate sustainability from certifications and materials"""
        evidence = []
        
        # Certifications
        cert_count = len(product_data.get('sustainability_certifications', []))
        cert_score = min(1.0, cert_count / 3)
        
        # Recycled content
        recycled_percentage = product_data.get('recycled_content_percent', 0) / 100
        
        # Carbon footprint
        carbon_kg = product_data.get('carbon_footprint_kg', 10)
        category_avg_carbon = product_data.get('category_avg_carbon_kg', 10)
        carbon_score = max(0, 1 - (carbon_kg / category_avg_carbon))
        
        # Packaging
        sustainable_packaging = product_data.get('sustainable_packaging', False)
        
        # Supply chain transparency
        supply_chain_score = product_data.get('supply_chain_transparency', 0.0)
        
        evidence.append(KPIEvidence(
            factor='recycled_content',
            value=recycled_percentage,
            source='product_specs',
            confidence=0.95,
            timestamp=datetime.now()
        ))
        
        evidence.append(KPIEvidence(
            factor='carbon_footprint_relative',
            value=carbon_score,
            source='lca_analysis',
            confidence=0.8,
            timestamp=datetime.now()
        ))
        
        score = min(1.0, 
            cert_score * 0.3 +
            recycled_percentage * 0.25 +
            carbon_score * 0.2 +
            (1.0 if sustainable_packaging else 0.0) * 0.1 +
            supply_chain_score * 0.15
        )
        
        return score, evidence
    
    def calculate_innovation_score(self, product_data: Dict) -> Tuple[float, List[KPIEvidence]]:
        """Calculate innovation from features and recognition"""
        evidence = []
        
        # New/unique features
        new_features = product_data.get('new_feature_count', 0)
        patent_count = product_data.get('patent_count', 0)
        
        # Awards and recognition
        awards = product_data.get('award_count', 0)
        press_mentions = product_data.get('press_mention_count', 0)
        
        # Technology adoption
        uses_new_tech = product_data.get('uses_cutting_edge_tech', False)
        tech_generation = product_data.get('tech_generation', 1)  # 1 = current, 2 = next-gen
        
        # First to market
        is_first_mover = product_data.get('is_first_in_category', False)
        
        evidence.append(KPIEvidence(
            factor='patent_count',
            value=patent_count,
            source='patent_database',
            confidence=1.0,
            timestamp=datetime.now()
        ))
        
        score = self._sigmoid(
            min(1.0, new_features / 3) * 0.25 +
            min(1.0, patent_count / 2) * 0.2 +
            min(1.0, awards / 2) * 0.15 +
            min(1.0, press_mentions / 10) * 0.1 +
            (1.0 if uses_new_tech else 0.0) * 0.15 +
            (tech_generation - 1) * 0.1 +
            (1.0 if is_first_mover else 0.0) * 0.05
        )
        
        return score, evidence
    
    def calculate_all_soft_signals(self, product_data: Dict, category: str = 'general') -> SoftSignals:
        """Calculate all soft signals for a product"""
        
        evidence_all = []
        
        # Calculate each score
        fit_score, fit_evidence = self.calculate_fit_hint_score(product_data)
        evidence_all.extend(fit_evidence)
        
        reliability_score, reliability_evidence = self.calculate_reliability_score(product_data)
        evidence_all.extend(reliability_evidence)
        
        performance_score, performance_evidence = self.calculate_performance_score(product_data, category)
        evidence_all.extend(performance_evidence)
        
        satisfaction_score, satisfaction_evidence = self.calculate_owner_satisfaction_score(product_data)
        evidence_all.extend(satisfaction_evidence)
        
        uniqueness_score, uniqueness_evidence = self.calculate_uniqueness_score(product_data)
        evidence_all.extend(uniqueness_evidence)
        
        craftsmanship_score, craftsmanship_evidence = self.calculate_craftsmanship_score(product_data)
        evidence_all.extend(craftsmanship_evidence)
        
        sustainability_score, sustainability_evidence = self.calculate_sustainability_score(product_data)
        evidence_all.extend(sustainability_evidence)
        
        innovation_score, innovation_evidence = self.calculate_innovation_score(product_data)
        evidence_all.extend(innovation_evidence)
        
        return SoftSignals(
            fit_hint_score=round(fit_score, 3),
            reliability_score=round(reliability_score, 3),
            performance_score=round(performance_score, 3),
            owner_satisfaction_score=round(satisfaction_score, 3),
            uniqueness_score=round(uniqueness_score, 3),
            craftsmanship_score=round(craftsmanship_score, 3),
            sustainability_score=round(sustainability_score, 3),
            innovation_score=round(innovation_score, 3),
            evidence=evidence_all,
            calculation_method='weighted_factors_sigmoid_normalized',
            last_updated=datetime.now()
        )
    
    def _sigmoid(self, x: float, steepness: float = 1.0) -> float:
        """Sigmoid function for normalization to [0,1]"""
        return 1 / (1 + math.exp(-steepness * x))
    
    def _z_score_normalize(self, value: float, mean: float, std: float) -> float:
        """Z-score normalization followed by sigmoid"""
        if std == 0:
            return 0.5
        z = (value - mean) / std
        return self._sigmoid(z)


# SQL templates for KPI data extraction
SQL_KPI_QUERIES = {
    'fit_metrics': """
        WITH return_analysis AS (
            SELECT 
                product_id,
                COUNT(*) AS returns_total,
                SUM(CASE WHEN reason = 'size_issue' THEN 1 ELSE 0 END) AS returns_size,
                SUM(CASE WHEN reason = 'size_issue' AND exchange_sku IS NOT NULL THEN 1 ELSE 0 END) AS exchanges_size
            FROM returns
            WHERE created_at >= CURRENT_DATE - INTERVAL '180 days'
            GROUP BY product_id
        ),
        purchase_behavior AS (
            SELECT
                oi.product_id,
                COUNT(DISTINCT o.id) AS purchases_total,
                SUM(CASE WHEN e.event_type = 'view_size_guide' THEN 1 ELSE 0 END) AS purchases_with_advisor
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            LEFT JOIN events e ON e.session_id = o.session_id 
                AND e.product_id = oi.product_id
                AND e.timestamp < o.created_at
            WHERE o.created_at >= CURRENT_DATE - INTERVAL '365 days'
            GROUP BY oi.product_id
        ),
        review_fit AS (
            SELECT
                product_id,
                COUNT(CASE WHEN aspects->>'fit' IS NOT NULL THEN 1 END) AS reviews_with_fit,
                COUNT(CASE WHEN (aspects->>'fit')::float >= 0.7 THEN 1 END) AS reviews_fit_positive
            FROM reviews
            WHERE created_at >= CURRENT_DATE - INTERVAL '365 days'
            GROUP BY product_id
        )
        SELECT 
            p.product_id,
            COALESCE(r.returns_total, 0) AS returns_total,
            COALESCE(r.returns_size, 0) AS returns_size,
            COALESCE(r.exchanges_size, 0) AS exchanges_size,
            COALESCE(pb.purchases_total, 0) AS purchases_total,
            COALESCE(pb.purchases_with_advisor, 0) AS purchases_with_advisor,
            COALESCE(rf.reviews_with_fit, 0) AS reviews_with_fit,
            COALESCE(rf.reviews_fit_positive, 0) AS reviews_fit_positive
        FROM products p
        LEFT JOIN return_analysis r ON r.product_id = p.id
        LEFT JOIN purchase_behavior pb ON pb.product_id = p.id
        LEFT JOIN review_fit rf ON rf.product_id = p.id
        WHERE p.id = %s
    """,
    
    'reliability_metrics': """
        WITH warranty_claims AS (
            SELECT
                product_id,
                COUNT(*) AS claim_count,
                COUNT(CASE WHEN claim_type = 'RMA' THEN 1 END) AS rma_count,
                AVG(EXTRACT(DAY FROM claim_date - purchase_date)) AS avg_days_to_claim
            FROM warranty_claims
            WHERE claim_date >= CURRENT_DATE - INTERVAL '2 years'
            GROUP BY product_id
        ),
        sales_data AS (
            SELECT
                product_id,
                SUM(quantity) AS units_sold
            FROM order_items
            WHERE created_at >= CURRENT_DATE - INTERVAL '2 years'
            GROUP BY product_id
        ),
        category_baseline AS (
            SELECT
                c.id AS category_id,
                AVG(wc.claim_count::float / NULLIF(sd.units_sold, 0) * 1000) AS category_rma_avg
            FROM categories c
            JOIN products p ON p.category_id = c.id
            LEFT JOIN warranty_claims wc ON wc.product_id = p.id
            LEFT JOIN sales_data sd ON sd.product_id = p.id
            GROUP BY c.id
        )
        SELECT
            p.id AS product_id,
            COALESCE(wc.claim_count, 0) AS claim_count,
            COALESCE(wc.rma_count, 0) AS rma_count,
            COALESCE(wc.avg_days_to_claim, 730) AS avg_days_to_claim,
            COALESCE(sd.units_sold, 0) AS units_sold,
            COALESCE(cb.category_rma_avg, 5.0) AS category_rma_avg,
            AVG(r.aspects->>'durability')::float AS reviews_durability_avg
        FROM products p
        LEFT JOIN warranty_claims wc ON wc.product_id = p.id
        LEFT JOIN sales_data sd ON sd.product_id = p.id
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN category_baseline cb ON cb.category_id = c.id
        LEFT JOIN reviews r ON r.product_id = p.id
        WHERE p.id = %s
        GROUP BY p.id, wc.claim_count, wc.rma_count, wc.avg_days_to_claim, 
                 sd.units_sold, cb.category_rma_avg
    """,
    
    'satisfaction_metrics': """
        WITH review_stats AS (
            SELECT
                product_id,
                AVG(rating) AS avg_rating,
                AVG(CASE WHEN verified_purchase THEN rating END) AS avg_rating_verified,
                COUNT(*) AS review_count_total,
                COUNT(CASE WHEN verified_purchase THEN 1 END) AS review_count_verified
            FROM reviews
            WHERE created_at >= CURRENT_DATE - INTERVAL '2 years'
            GROUP BY product_id
        ),
        csat_data AS (
            SELECT
                product_id,
                AVG(score) AS csat_product,
                COUNT(*) AS csat_responses
            FROM customer_satisfaction
            WHERE survey_type = 'product'
                AND created_at >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY product_id
        ),
        sentiment_trends AS (
            SELECT
                product_id,
                AVG(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '90 days' 
                    THEN sentiment_score END) AS sentiment_90d,
                AVG(CASE WHEN created_at < CURRENT_DATE - INTERVAL '90 days' 
                    AND created_at >= CURRENT_DATE - INTERVAL '180 days'
                    THEN sentiment_score END) AS sentiment_prev_90d
            FROM reviews
            WHERE created_at >= CURRENT_DATE - INTERVAL '180 days'
            GROUP BY product_id
        ),
        repeat_purchases AS (
            SELECT
                oi.product_id,
                COUNT(DISTINCT CASE WHEN purchase_number > 1 THEN customer_id END)::float 
                    / NULLIF(COUNT(DISTINCT customer_id), 0) AS repeat_purchase_rate
            FROM (
                SELECT 
                    oi.product_id,
                    o.customer_id,
                    ROW_NUMBER() OVER (PARTITION BY o.customer_id, oi.product_id ORDER BY o.created_at) AS purchase_number
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
            ) oi
            GROUP BY oi.product_id
        )
        SELECT
            p.id AS product_id,
            rs.avg_rating,
            rs.avg_rating_verified,
            rs.review_count_total,
            rs.review_count_verified,
            COALESCE(cs.csat_product, 0.7) AS csat_product,
            COALESCE(cs.csat_responses, 0) AS csat_responses,
            COALESCE(st.sentiment_90d, 0.5) AS sentiment_90d,
            COALESCE(st.sentiment_prev_90d, 0.5) AS sentiment_prev_90d,
            COALESCE(rp.repeat_purchase_rate, 0.1) AS repeat_purchase_rate
        FROM products p
        LEFT JOIN review_stats rs ON rs.product_id = p.id
        LEFT JOIN csat_data cs ON cs.product_id = p.id
        LEFT JOIN sentiment_trends st ON st.product_id = p.id
        LEFT JOIN repeat_purchases rp ON rp.product_id = p.id
        WHERE p.id = %s
    """
}
