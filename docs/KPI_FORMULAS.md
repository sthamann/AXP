# AXP KPI Formulas and Measurement Standards

## Overview

This document defines normative formulas and measurement windows for all KPIs in the AXP protocol. All implementations MUST follow these calculations to ensure consistency across the ecosystem.

## Core Business KPIs

### Return Rate
```
return_rate = returns_in_window / units_shipped_in_window

Window: 90 days rolling
Update frequency: Daily
Minimum sample size: 10 shipments
```

### Dispute Rate
```
dispute_rate = payment_disputes_in_window / orders_in_window

Window: 180 days rolling
Update frequency: Weekly
Minimum sample size: 50 orders
```

### Chargeback Rate
```
chargeback_rate = chargebacks_in_window / transactions_in_window

Window: 180 days rolling
Update frequency: Weekly
Minimum sample size: 100 transactions
Warning threshold: > 0.01 (1%)
```

### On-Time Delivery Rate
```
on_time_rate = deliveries_on_promised_date / total_deliveries

Window: 30 days rolling
Update frequency: Daily
Minimum sample size: 20 deliveries
```

### Customer Satisfaction (CSAT)
```
csat = satisfied_responses / total_responses
(satisfied = ratings >= 4 on 5-point scale)

Window: 90 days rolling
Update frequency: Weekly
Minimum responses: 30
```

### Net Promoter Score (NPS)
```
nps = promoters_percent - detractors_percent
(promoters = 9-10, detractors = 0-6 on 0-10 scale)

Window: 90 days rolling
Update frequency: Monthly
Minimum responses: 50
```

### First Response Time (Support)
```
first_response_hours = median(ticket_first_response_time)

Window: 30 days rolling
Update frequency: Daily
Percentiles: p50, p95
```

## Intent Signal Measurements

### Intent Share Calculation
```
intent_share = intent_events / total_qualifying_events

Qualifying events: purchase, add_to_cart, configure, extended_view (>30s)
Window: 90 days rolling for most intents
Window: 365 days for seasonal intents (gift, holiday)
Minimum events: 100
```

### Intent Confidence (Wilson Score)
```python
def wilson_score_confidence(positive, total, z=1.96):
    """
    Calculate Wilson score confidence interval
    z = 1.96 for 95% confidence
    """
    if total == 0:
        return 0.0
    
    phat = positive / total
    denominator = 1 + z**2 / total
    
    center = (phat + z**2 / (2*total)) / denominator
    spread = z * sqrt((phat*(1-phat) + z**2/(4*total)) / total) / denominator
    
    lower_bound = center - spread
    return max(0, lower_bound)  # Use lower bound as conservative estimate
```

### Event Attribution Windows
- **View to Cart**: 1 hour
- **Cart to Purchase**: 7 days
- **Support to Return**: 30 days
- **Purchase to Review**: 90 days

## Product Performance Scores

### Fit Hint Score
```
fit_hint_score = 1 - (size_returns / total_sales)

Adjustments:
- Weight by return reason (size = 1.0, other = 0.2)
- Normalize by category baseline
Window: 180 days
Minimum sales: 20
```

### Reliability Score
```
reliability_score = 1 - (weighted_failure_rate)

weighted_failure_rate = 
    (0.5 * warranty_claims / units_sold) +
    (0.3 * support_tickets_product / units_sold) +
    (0.2 * quality_returns / units_sold)

Window: 365 days
Minimum units: 50
```

### Performance Score (Category-Specific)

#### Electronics
```
performance_score = weighted_average(
    benchmark_percentile * 0.4,
    efficiency_rating * 0.3,
    feature_completeness * 0.3
)
```

#### Footwear
```
performance_score = weighted_average(
    energy_return_percent * 0.35,
    weight_index * 0.25,
    cushioning_rating * 0.25,
    durability_score * 0.15
)
```

#### Apparel
```
performance_score = weighted_average(
    fabric_quality * 0.35,
    fit_consistency * 0.25,
    color_fastness * 0.20,
    comfort_rating * 0.20
)
```

### Owner Satisfaction Score
```
owner_satisfaction = weighted_average(
    verified_review_avg * 1.5,  # 1.5x weight for verified
    unverified_review_avg * 1.0,
    repeat_purchase_rate * 2.0,
    recommendation_rate * 1.5
) / total_weight

Window: 90 days for recent trend
Window: All-time for baseline
Trend weight: 0.7 * recent + 0.3 * baseline
```

## Trust Signal Calculations

### Brand Trust Score
```
brand_trust = weighted_average(
    domain_age_score * 0.15,
    certification_score * 0.20,
    review_authenticity * 0.25,
    dispute_resolution * 0.20,
    transparency_score * 0.20
)

Where:
- domain_age_score = min(1.0, domain_age_days / 1095)  # 3 years = max
- certification_score = valid_certs / total_possible_certs
- review_authenticity = verified_reviews / total_reviews
- dispute_resolution = resolved_disputes / total_disputes
- transparency_score = provided_fields / required_fields
```

### Review Authenticity Score
```
authenticity_score = weighted_factors(
    verified_purchase_rate * 0.40,
    text_originality_score * 0.30,
    reviewer_history_score * 0.20,
    timing_distribution_score * 0.10
)

Anomaly flags:
- > 50 reviews in 24 hours
- > 80% five-star in single batch
- Duplicate text patterns > 20%
```

## Statistical Methods

### Time Decay for Historical Data
```
weight = exp(-lambda * age_in_days)

Lambda values by signal type:
- Behavioral signals: λ = 0.0077 (90-day half-life)
- Transaction signals: λ = 0.0039 (180-day half-life)
- Review signals: λ = 0.0019 (365-day half-life)
```

### Dirichlet Smoothing for Sparse Data
```
smoothed_score = (n * raw_score + alpha * prior) / (n + alpha)

Where:
- n = sample size
- alpha = smoothing parameter (typically 10-50)
- prior = category average or 0.5 if unknown
```

### Anomaly Detection Thresholds
```
is_anomaly = |current - baseline| > threshold * std_dev

Thresholds:
- Rating change: 2.5 * std_dev
- Volume change: 3.0 * std_dev
- Return rate change: 2.0 * std_dev
```

## Caching and Update Strategies

### Update Frequencies (MUST)
- Real-time: Inventory, pricing (< 1 minute)
- Hourly: Cart metrics, session data
- Daily: Return rate, delivery metrics
- Weekly: Dispute rate, trust scores
- Monthly: NPS, brand strength

### Cache Keys
```
cache_key = f"{metric_type}:{entity_id}:{window}:{hash(params)}"

Invalidation triggers:
- Price change > 5%
- Stock state change
- Review count increase > 10
- New certification/revocation
```

### Minimum Sample Sizes (SHOULD)
- Intent signals: 100 events
- Return rate: 10 shipments
- Review scores: 5 reviews
- NPS: 50 responses
- Trust scores: 30 data points

## Compliance and Reporting

### Required Audit Fields
Every calculated KPI MUST include:
```json
{
  "value": 0.85,
  "window_days": 90,
  "sample_size": 1234,
  "confidence": 0.95,
  "method": "wilson_score",
  "calculated_at": "2025-09-18T10:00:00Z",
  "ttl_seconds": 86400
}
```

### Data Retention
- Raw events: 24 months minimum
- Aggregated KPIs: 36 months minimum
- Anomaly records: Indefinite
- Audit logs: 7 years

## Implementation Notes

1. **Rounding**: All public scores MUST be rounded to 2 decimal places
2. **Null handling**: Missing data should not default to 0; use null
3. **Confidence intervals**: Always provide when sample size < 100
4. **Trend indicators**: Include direction and velocity for time-series data
5. **Benchmarking**: Compare against category medians when available

---

*This specification is normative. All AXP implementations MUST follow these formulas for consistency.*
