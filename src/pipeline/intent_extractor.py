"""
AXP Intent Signal Extraction Pipeline
Robust extraction and calculation of intent signals from shop data
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import hashlib
import math
from dataclasses import dataclass
from collections import defaultdict


class IntentType(Enum):
    """Canonical intent taxonomy"""
    GIFT = "gift"
    DAILY_COMMUTE = "daily_commute" 
    HOBBY = "hobby"
    PROFESSIONAL_USE = "professional_use"
    TRAVEL = "travel"
    FASHION = "fashion"
    SPORT = "sport"
    BASKETBALL = "basketball"
    RUNNING = "running"
    OUTDOOR = "outdoor"
    LUXURY = "luxury"
    VALUE = "value"


@dataclass
class IntentSignal:
    intent: str
    share: float
    confidence: float
    method: str
    evidence: List[str]
    last_updated: datetime


class IntentExtractor:
    """Extract intent signals from multiple data sources"""
    
    def __init__(self, 
                 text_weight: float = 0.4,
                 behavior_weight: float = 0.25,
                 cart_weight: float = 0.25,
                 channel_weight: float = 0.1,
                 recency_half_life_days: int = 90):
        
        self.weights = {
            'text': text_weight,
            'behavior': behavior_weight,
            'cart': cart_weight,
            'channel': channel_weight
        }
        self.recency_half_life_days = recency_half_life_days
        self.dirichlet_alpha = 0.5
        
    def extract_from_orders(self, product_id: str, orders: List[Dict]) -> Dict[str, float]:
        """Extract intent signals from order context"""
        intent_scores = defaultdict(float)
        total_orders = len(orders)
        
        if total_orders == 0:
            return {}
            
        for order in orders:
            # Gift indicators
            if order.get('gift_wrap') or order.get('gift_message'):
                intent_scores[IntentType.GIFT.value] += 1
                
            # Time of order (holiday seasons)
            order_date = datetime.fromisoformat(order['created_at'])
            if self._is_holiday_season(order_date):
                intent_scores[IntentType.GIFT.value] += 0.3
                
            # Bundle analysis - what was bought together
            if 'items' in order:
                bundle_intent = self._analyze_bundle(order['items'])
                for intent, score in bundle_intent.items():
                    intent_scores[intent] += score
                    
        # Normalize
        for intent in intent_scores:
            intent_scores[intent] /= total_orders
            
        return dict(intent_scores)
    
    def extract_from_returns(self, product_id: str, returns: List[Dict]) -> Dict[str, float]:
        """Extract negative signals from return data"""
        intent_adjustments = defaultdict(float)
        
        for return_item in returns:
            reason = return_item.get('reason', '')
            
            # Size issues suggest fashion/sport intent (fit matters)
            if reason == 'size_issue':
                intent_adjustments[IntentType.FASHION.value] += 0.1
                intent_adjustments[IntentType.SPORT.value] += 0.1
                
            # Quality expectations suggest professional use
            elif reason == 'quality_expectation':
                intent_adjustments[IntentType.PROFESSIONAL_USE.value] += 0.2
                
            # Changed mind often correlates with impulse/fashion
            elif reason == 'changed_mind':
                intent_adjustments[IntentType.FASHION.value] += 0.15
                
        return dict(intent_adjustments)
    
    def extract_from_behavior(self, product_id: str, events: List[Dict]) -> Dict[str, float]:
        """Extract intent from onsite behavior"""
        intent_scores = defaultdict(float)
        event_count = defaultdict(int)
        
        for event in events:
            event_type = event['type']
            event_count[event_type] += 1
            
            # Specific tool usage indicates intent
            if event_type == 'view_size_guide':
                intent_scores[IntentType.FASHION.value] += 0.3
                intent_scores[IntentType.SPORT.value] += 0.2
                
            elif event_type == 'view_3d':
                intent_scores[IntentType.FASHION.value] += 0.2
                intent_scores[IntentType.LUXURY.value] += 0.1
                
            elif event_type == 'use_configurator':
                intent_scores[IntentType.PROFESSIONAL_USE.value] += 0.3
                intent_scores[IntentType.HOBBY.value] += 0.2
                
            elif event_type == 'compare_products':
                intent_scores[IntentType.VALUE.value] += 0.2
                
            elif event_type == 'read_guide' and 'guide_type' in event:
                guide = event['guide_type']
                if 'running' in guide.lower():
                    intent_scores[IntentType.RUNNING.value] += 0.5
                elif 'basketball' in guide.lower():
                    intent_scores[IntentType.BASKETBALL.value] += 0.5
                    
        # Normalize by event frequency
        total_events = sum(event_count.values())
        if total_events > 0:
            for intent in intent_scores:
                intent_scores[intent] /= math.sqrt(total_events)
                
        return dict(intent_scores)
    
    def extract_from_text(self, product_id: str, texts: List[Dict]) -> Dict[str, float]:
        """Extract intent from reviews, Q&A, support tickets"""
        intent_scores = defaultdict(float)
        
        # Simplified keyword-based classification (in production: use proper NLP model)
        intent_keywords = {
            IntentType.GIFT.value: ['gift', 'present', 'birthday', 'christmas', 'anniversary'],
            IntentType.SPORT.value: ['running', 'training', 'workout', 'gym', 'athletic'],
            IntentType.PROFESSIONAL_USE.value: ['work', 'professional', 'office', 'business', 'daily'],
            IntentType.TRAVEL.value: ['travel', 'trip', 'vacation', 'flight', 'luggage'],
            IntentType.FASHION.value: ['style', 'look', 'outfit', 'trendy', 'fashion'],
            IntentType.DAILY_COMMUTE.value: ['commute', 'daily', 'everyday', 'walking', 'comfortable']
        }
        
        for text_item in texts:
            content = text_item.get('text', '').lower()
            weight = self._get_text_weight(text_item)
            
            for intent, keywords in intent_keywords.items():
                matches = sum(1 for kw in keywords if kw in content)
                if matches > 0:
                    intent_scores[intent] += matches * weight
                    
        # Apply zero-shot classification scores if available
        if texts and 'intent_probs' in texts[0]:
            for text_item in texts:
                for intent, prob in text_item['intent_probs'].items():
                    intent_scores[intent] += prob * self._get_text_weight(text_item)
                    
        # Normalize
        total_weight = sum(self._get_text_weight(t) for t in texts)
        if total_weight > 0:
            for intent in intent_scores:
                intent_scores[intent] /= total_weight
                
        return dict(intent_scores)
    
    def extract_from_channel(self, product_id: str, acquisitions: List[Dict]) -> Dict[str, float]:
        """Extract intent from acquisition channels"""
        intent_scores = defaultdict(float)
        
        for acq in acquisitions:
            campaign = acq.get('utm_campaign', '').lower()
            source = acq.get('utm_source', '').lower()
            term = acq.get('utm_term', '').lower()
            landing = acq.get('landing_page', '').lower()
            
            # Campaign-based intent
            if 'gift' in campaign or 'holiday' in campaign:
                intent_scores[IntentType.GIFT.value] += 1
            elif 'sport' in campaign or 'athletic' in campaign:
                intent_scores[IntentType.SPORT.value] += 1
            elif 'professional' in campaign or 'business' in campaign:
                intent_scores[IntentType.PROFESSIONAL_USE.value] += 1
                
            # Search terms
            if term:
                for intent_type in IntentType:
                    if intent_type.value.replace('_', ' ') in term:
                        intent_scores[intent_type.value] += 0.5
                        
        # Normalize
        total_acquisitions = len(acquisitions)
        if total_acquisitions > 0:
            for intent in intent_scores:
                intent_scores[intent] /= total_acquisitions
                
        return dict(intent_scores)
    
    def compute_intent_signals(self, 
                              product_id: str,
                              data_sources: Dict[str, Any],
                              since_days: int = 365) -> List[IntentSignal]:
        """
        Compute final intent signals by mixing all sources
        
        Args:
            product_id: Product identifier
            data_sources: Dict with keys 'orders', 'returns', 'events', 'texts', 'acquisitions'
            since_days: Time window for data consideration
            
        Returns:
            List of IntentSignal objects with shares summing to 1.0
        """
        
        # Extract from each source
        order_intents = self.extract_from_orders(product_id, data_sources.get('orders', []))
        return_intents = self.extract_from_returns(product_id, data_sources.get('returns', []))
        behavior_intents = self.extract_from_behavior(product_id, data_sources.get('events', []))
        text_intents = self.extract_from_text(product_id, data_sources.get('texts', []))
        channel_intents = self.extract_from_channel(product_id, data_sources.get('acquisitions', []))
        
        # Mix sources with time decay
        all_intents = set()
        all_intents.update(order_intents.keys())
        all_intents.update(return_intents.keys())
        all_intents.update(behavior_intents.keys())
        all_intents.update(text_intents.keys())
        all_intents.update(channel_intents.keys())
        
        mixed_scores = {}
        for intent in all_intents:
            score = 0
            score += self.weights['cart'] * order_intents.get(intent, 0)
            score += self.weights['cart'] * return_intents.get(intent, 0) * 0.5  # Returns are negative signal
            score += self.weights['behavior'] * behavior_intents.get(intent, 0)
            score += self.weights['text'] * text_intents.get(intent, 0)
            score += self.weights['channel'] * channel_intents.get(intent, 0)
            
            # Apply time decay
            score *= self._compute_time_weight(since_days)
            mixed_scores[intent] = score
            
        # Dirichlet smoothing
        smoothed_scores = self._dirichlet_smooth(mixed_scores, len(IntentType))
        
        # Create IntentSignal objects
        signals = []
        for intent, share in smoothed_scores.items():
            evidence = []
            if intent in order_intents:
                evidence.append(f"orders:{order_intents[intent]:.2f}")
            if intent in text_intents:
                evidence.append(f"text:{text_intents[intent]:.2f}")
            if intent in behavior_intents:
                evidence.append(f"behavior:{behavior_intents[intent]:.2f}")
                
            signal = IntentSignal(
                intent=intent,
                share=share,
                confidence=self._compute_confidence(data_sources),
                method=f"mixed_weights:{self.weights}",
                evidence=evidence,
                last_updated=datetime.now()
            )
            signals.append(signal)
            
        # Sort by share descending
        signals.sort(key=lambda s: s.share, reverse=True)
        
        return signals
    
    def _analyze_bundle(self, items: List[Dict]) -> Dict[str, float]:
        """Analyze product bundles for intent patterns"""
        bundle_intents = defaultdict(float)
        
        # Simple heuristics - in production use association rules
        categories = [item.get('category', '') for item in items]
        
        if 'running_shoes' in categories and 'running_socks' in categories:
            bundle_intents[IntentType.RUNNING.value] += 0.8
            bundle_intents[IntentType.SPORT.value] += 0.5
            
        if 'dress_shoes' in categories and 'dress_shirt' in categories:
            bundle_intents[IntentType.PROFESSIONAL_USE.value] += 0.7
            
        return dict(bundle_intents)
    
    def _is_holiday_season(self, date: datetime) -> bool:
        """Check if date falls in typical gift-giving season"""
        month_day = (date.month, date.day)
        
        # Christmas season
        if (11, 15) <= month_day <= (12, 31):
            return True
        # Valentine's
        if (2, 1) <= month_day <= (2, 14):
            return True
        # Mother's/Father's day (approximate)
        if (5, 1) <= month_day <= (5, 31) or (6, 1) <= month_day <= (6, 20):
            return True
            
        return False
    
    def _get_text_weight(self, text_item: Dict) -> float:
        """Weight text by source and verification status"""
        base_weight = 1.0
        
        if text_item.get('verified_purchase'):
            base_weight *= 1.5
            
        source = text_item.get('source', 'review')
        if source == 'support_ticket':
            base_weight *= 0.8
        elif source == 'q_and_a':
            base_weight *= 1.1
            
        return base_weight
    
    def _compute_time_weight(self, days_ago: int) -> float:
        """Exponential decay weight based on recency"""
        return math.exp(-days_ago / self.recency_half_life_days)
    
    def _dirichlet_smooth(self, scores: Dict[str, float], num_classes: int) -> Dict[str, float]:
        """Apply Dirichlet smoothing for small sample sizes"""
        total = sum(scores.values())
        smoothed = {}
        
        for intent in scores:
            count = scores[intent] * 100  # Scale to pseudo-counts
            smoothed[intent] = (count + self.dirichlet_alpha) / (total * 100 + num_classes * self.dirichlet_alpha)
            
        # Add small probability for unseen intents
        for intent_type in IntentType:
            if intent_type.value not in smoothed:
                smoothed[intent_type.value] = self.dirichlet_alpha / (total * 100 + num_classes * self.dirichlet_alpha)
                
        # Normalize to sum to 1
        total_smoothed = sum(smoothed.values())
        for intent in smoothed:
            smoothed[intent] /= total_smoothed
            
        return smoothed
    
    def _compute_confidence(self, data_sources: Dict) -> float:
        """Compute confidence score based on data availability"""
        confidence = 0.0
        weights = {'orders': 0.3, 'events': 0.2, 'texts': 0.3, 'returns': 0.1, 'acquisitions': 0.1}
        
        for source, weight in weights.items():
            if source in data_sources and len(data_sources[source]) > 0:
                # More data = higher confidence (with diminishing returns)
                n = len(data_sources[source])
                confidence += weight * min(1.0, math.log(n + 1) / math.log(100))
                
        return min(1.0, confidence)


# SQL query templates for data extraction
SQL_QUERIES = {
    'intent_from_returns': """
        SELECT 
            product_id,
            SUM(CASE WHEN return_reason = 'size_issue' THEN 1 ELSE 0 END)::FLOAT 
                / NULLIF(COUNT(*), 0) AS p_size_issue,
            SUM(CASE WHEN return_reason = 'quality_expectation' THEN 1 ELSE 0 END)::FLOAT
                / NULLIF(COUNT(*), 0) AS p_quality_issue  
        FROM returns
        WHERE return_date >= CURRENT_DATE - INTERVAL '180 days'
        GROUP BY product_id
    """,
    
    'gift_proxy': """
        SELECT 
            product_id,
            AVG(CASE WHEN gift_wrap = TRUE OR gift_message IS NOT NULL THEN 1 ELSE 0 END) AS p_gift,
            COUNT(*) AS order_count
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.created_at >= CURRENT_DATE - INTERVAL '365 days'
        GROUP BY product_id
    """,
    
    'behavior_events': """
        SELECT
            product_id,
            event_type,
            COUNT(*) AS event_count,
            COUNT(DISTINCT session_id) AS unique_sessions
        FROM user_events
        WHERE timestamp >= CURRENT_DATE - INTERVAL '90 days'
            AND product_id = %s
        GROUP BY product_id, event_type
    """,
    
    'channel_attribution': """
        SELECT
            oi.product_id,
            s.utm_campaign,
            s.utm_source,
            s.utm_term,
            s.landing_page,
            COUNT(*) AS acquisition_count
        FROM sessions s
        JOIN orders o ON o.session_id = s.id
        JOIN order_items oi ON oi.order_id = o.id
        WHERE s.created_at >= CURRENT_DATE - INTERVAL '180 days'
            AND oi.product_id = %s
        GROUP BY oi.product_id, s.utm_campaign, s.utm_source, s.utm_term, s.landing_page
    """
}


def example_usage():
    """Example of intent extraction pipeline"""
    
    extractor = IntentExtractor()
    
    # Mock data sources
    data_sources = {
        'orders': [
            {'created_at': '2025-12-20T10:00:00Z', 'gift_wrap': True, 'items': []},
            {'created_at': '2025-09-15T10:00:00Z', 'gift_wrap': False, 'items': [
                {'category': 'running_shoes'},
                {'category': 'running_socks'}
            ]}
        ],
        'returns': [
            {'reason': 'size_issue', 'created_at': '2025-09-10T10:00:00Z'},
        ],
        'events': [
            {'type': 'view_size_guide', 'timestamp': '2025-09-01T10:00:00Z'},
            {'type': 'view_3d', 'timestamp': '2025-09-01T11:00:00Z'},
            {'type': 'read_guide', 'guide_type': 'running_tips', 'timestamp': '2025-09-02T10:00:00Z'}
        ],
        'texts': [
            {'text': 'Great running shoe for my daily training', 'verified_purchase': True, 'source': 'review'},
            {'text': 'Bought as a gift for my husband', 'verified_purchase': True, 'source': 'review'}
        ],
        'acquisitions': [
            {'utm_campaign': 'sport_sale', 'utm_source': 'google', 'utm_term': 'running shoes'},
            {'utm_campaign': 'holiday_gifts', 'utm_source': 'email', 'landing_page': '/gifts'}
        ]
    }
    
    signals = extractor.compute_intent_signals('sku_123', data_sources)
    
    for signal in signals:
        print(f"{signal.intent}: {signal.share:.2%} (confidence: {signal.confidence:.2f})")
        print(f"  Evidence: {', '.join(signal.evidence)}")
        print(f"  Method: {signal.method}")
        print()


if __name__ == '__main__':
    example_usage()
