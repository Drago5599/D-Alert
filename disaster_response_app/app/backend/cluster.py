import math
from datetime import timedelta
from typing import List
from app.backend.models import Alert

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def update_clusters_and_risk(session, new_alert: Alert):
    # Find nearby alerts within 2km and 60min
    # Note: In a real DB we'd use PostGIS, here we fetch active alerts and filter in python
    # Ideally filter by roughly bounding box first if DB gets large

    time_threshold = new_alert.timestamp_utc - timedelta(minutes=60)

    # Fetch potential neighbors (simple filter)
    candidates = session.query(Alert).filter(
        Alert.status != "resolved",
        Alert.timestamp_utc >= time_threshold
    ).all()

    neighbors = []
    for cand in candidates:
        if cand.id == new_alert.id:
            continue
        if cand.lat is None or new_alert.lat is None:
            continue

        dist = haversine(new_alert.lat, new_alert.lon, cand.lat, cand.lon)
        if dist <= 2.0: # 2km
            neighbors.append(cand)

    # Cluster ID logic
    if neighbors:
        # Join existing cluster or create new based on first neighbor
        cluster_id = neighbors[0].cluster_id
        if not cluster_id:
            # Create a simple hash ID if none exists
            cluster_id = f"cls_{abs(hash(str(new_alert.timestamp_utc) + str(new_alert.lat)))}"
            neighbors[0].cluster_id = cluster_id
            session.add(neighbors[0])

        new_alert.cluster_id = cluster_id

    # Recalculate Risk for New Alert
    # Note: In a full system, we might trigger re-calc for all neighbors too
    from app.backend.risk import calculate_risk_score

    new_alert.risk_score = calculate_risk_score(
        new_alert.severity,
        new_alert.confidence,
        new_alert.timestamp_utc,
        len(neighbors)
    )

    session.add(new_alert)
    session.commit()
