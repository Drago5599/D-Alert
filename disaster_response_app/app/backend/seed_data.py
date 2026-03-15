import json
import os
import requests

# Assuming running from root via: python -m app.backend.seed_data

def load_seed_data():
    base_url = "http://localhost:8000"

    # Build robust paths to data files
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    social_seed_path = os.path.join(project_root, "data", "social_seed.json")
    weather_seed_path = os.path.join(project_root, "data", "weather_seed.json")


    # Load Social Data
    print("Loading Social Data...")
    try:
        with open(social_seed_path, "r") as f:
            social_data = json.load(f)

        for item in social_data:
            try:
                response = requests.post(f"{base_url}/ingest/social", json=item)
                response.raise_for_status()
                print(f"Posted: {item['text'][:20]}...")
            except Exception as e:
                print(f"Error posting: {e}")
    except FileNotFoundError:
        print(f"social_seed.json not found at {social_seed_path}")

    # Load Weather Data
    print("Loading Weather Data...")
    try:
        with open(weather_seed_path, "r") as f:
            weather_data = json.load(f)

        for item in weather_data:
            try:
                response = requests.post(f"{base_url}/ingest/weather", json=item)
                response.raise_for_status()
                print(f"Posted Weather: {item['headline'][:20]}...")
            except Exception as e:
                print(f"Error posting weather: {e}")
    except FileNotFoundError:
        print(f"weather_seed.json not found at {weather_seed_path}")

if __name__ == "__main__":
    # Ensure server is running first!
    print("Ensure uvicorn is running on port 8000!")
    try:
        load_seed_data()
        print("Seeding Complete.")
    except Exception as e:
        print(f"Failed. Is the backend running? {e}")
