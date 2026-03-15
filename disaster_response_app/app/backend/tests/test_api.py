from fastapi.testclient import TestClient
from app.backend.main import app

client = TestClient(app)

def test_ingest_social_happy_path():
    payload = {
        "text": "Huge fire near the gas station",
        "location_name": "Kingston"
    }
    response = client.post("/ingest/social", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["disaster_type"] == "fire"
    assert data["severity"] == 3 # 'fire' is high severity
    assert data["location_name"] == "Kingston"
    assert "id" in data

def test_ingest_social_deduplication():
    payload = {
        "text": "The river is rising fast!",
        "location_name": "Spanish Town"
    }
    # Send 3 reports, should be accepted
    for _ in range(3):
        response = client.post("/ingest/social", json=payload)
        assert response.status_code == 200

    # 4th report should be rejected
    response = client.post("/ingest/social", json=payload)
    assert response.status_code == 429
    assert response.json()["detail"] == "Duplicate report threshold met"
