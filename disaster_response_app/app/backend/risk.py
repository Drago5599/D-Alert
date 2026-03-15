from datetime import datetime, timedelta

def calculate_risk_score(severity: int, confidence: float, timestamp: datetime, nearby_count: int):
    """
    risk_score = (severity_weight * severity) + (0.6 * confidence) + (recency_boost) + (cluster_density_boost)
    """
    severity_weight = 1.5

    # Recency Boost
    now = datetime.utcnow()
    age = now - timestamp
    recency_boost = 0.0
    if age < timedelta(minutes=30):
        recency_boost = 0.5
    elif age < timedelta(hours=2):
        recency_boost = 0.2

    # Cluster Density Boost
    # Cap at 0.8
    cluster_density_boost = min(0.8, 0.2 * nearby_count)

    score = (severity_weight * severity) + (0.6 * confidence) + recency_boost + cluster_density_boost
    return round(score, 2)
