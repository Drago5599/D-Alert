from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, desc
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from app.backend.db import create_db_and_tables, get_session
from app.backend.models import Alert, AlertCreate, AlertRead
from app.backend.classify import classify_alert
from app.backend.geocode_demo import geocode_location
from app.backend.cluster import update_clusters_and_risk

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest/social", response_model=AlertRead)
def ingest_social(data: dict, session: Session = Depends(get_session)):
    text = data.get("text")
    location_name = data.get("location_name")

    if not text:
        raise HTTPException(status_code=400, detail="Text required")

    # Deduplication check
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    statement = select(Alert).where(
        Alert.raw_text == text,
        Alert.location_name == location_name,
        Alert.timestamp_utc >= one_hour_ago
    )
    results = session.exec(statement).all()
    if len(results) >= 3:
        raise HTTPException(status_code=429, detail="Duplicate report threshold met")

    # Classify
    classification = classify_alert(text)

    # Geocode
    lat, lon = data.get("lat"), data.get("lon")
    if not lat or not lon:
        lat, lon = geocode_location(location_name)

    alert = Alert(
        source="social",
        raw_text=text,
        location_name=location_name,
        lat=lat,
        lon=lon,
        disaster_type=classification["disaster_type"],
        severity=classification["severity"],
        confidence=classification["confidence"],
        suggested_action=classification["suggested_action"],
        timestamp_utc=datetime.utcnow()
    )

    session.add(alert)
    session.commit()
    session.refresh(alert)

    # Calculate Risk & Cluster
    update_clusters_and_risk(session, alert)
    session.refresh(alert)

    return alert

@app.post("/ingest/weather", response_model=AlertRead)
def ingest_weather(data: dict, session: Session = Depends(get_session)):
    headline = data.get("headline", "")
    area = data.get("areaDesc", "")
    severity = data.get("severity", 2)

    # Geocode
    lat, lon = geocode_location(area)

    alert = Alert(
        source="weather",
        raw_text=f"{data.get('event')}: {headline}",
        location_name=area,
        lat=lat,
        lon=lon,
        disaster_type="weather_alert",
        severity=severity,
        confidence=1.0, # Official source
        suggested_action="Follow official guidance.",
        timestamp_utc=datetime.utcnow()
    )

    session.add(alert)
    session.commit()
    session.refresh(alert)

    update_clusters_and_risk(session, alert)
    session.refresh(alert)

    return alert

@app.get("/alerts", response_model=List[AlertRead])
def get_alerts(
    status: Optional[str] = None,
    disaster_type: Optional[str] = None,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    query = select(Alert).order_by(desc(Alert.timestamp_utc))
    if status:
        query = query.where(Alert.status == status)
    if disaster_type:
        query = query.where(Alert.disaster_type == disaster_type)

    results = session.exec(query.limit(limit)).all()
    return results

@app.get("/priorities", response_model=List[AlertRead])
def get_priorities(session: Session = Depends(get_session)):
    # Top 20 unresolved by risk score
    query = select(Alert).where(Alert.status != "resolved").order_by(desc(Alert.risk_score)).limit(20)
    results = session.exec(query).all()
    return results

@app.post("/alerts/{alert_id}/ack")
def acknowledge_alert(alert_id: str, session: Session = Depends(get_session)):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "acknowledged"
    session.add(alert)
    session.commit()
    return {"ok": True}

@app.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: str, session: Session = Depends(get_session)):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "resolved"
    session.add(alert)
    session.commit()
    return {"ok": True}

@app.get("/clusters")
def get_clusters(session: Session = Depends(get_session)):
    # Simple aggregation for demo
    # Returns clusters with > 1 item
    alerts = session.exec(select(Alert).where(Alert.cluster_id != None)).all()

    clusters = {}
    for a in alerts:
        if a.cluster_id not in clusters:
            clusters[a.cluster_id] = {"count": 0, "lat_sum": 0, "lon_sum": 0, "risk_sum": 0}

        c = clusters[a.cluster_id]
        c["count"] += 1
        c["lat_sum"] += (a.lat or 0)
        c["lon_sum"] += (a.lon or 0)
        c["risk_sum"] += a.risk_score

    result = []
    for cid, data in clusters.items():
        if data["count"] > 0:
            result.append({
                "cluster_id": cid,
                "count": data["count"],
                "lat": data["lat_sum"] / data["count"],
                "lon": data["lon_sum"] / data["count"],
                "avg_risk": round(data["risk_sum"] / data["count"], 2)
            })
    return result
