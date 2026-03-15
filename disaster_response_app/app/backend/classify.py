import os
import json
from openai import OpenAI

# Keywords for rule-based classifier
KEYWORDS = {
    "flood": ["flood", "water rising", "rain", "drowning", "stuck in water"],
    "fire": ["fire", "smoke", "burning", "flames"],
    "landslide": ["landslide", "mud", "debris", "rock slide", "slope"],
    "hurricane": ["wind", "storm", "hurricane", "gust", "roof"],
    "medical": ["injury", "hurt", "blood", "ambulance",  "medical", "unconscious"],
}

SEVERITY_HIGH = ["trapped", "can't escape", "cars floating", "fire","critical", "collapsed", "blood", "death"]
SEVERITY_MED = ["blocked", "damage", "stuck", "rising"]

def classify_text_rules(text: str):
    text_lower = text.lower()

    # Detect Type
    disaster_type = "other"
    for dtype, words in KEYWORDS.items():
        if any(w in text_lower for w in words):
            disaster_type = dtype
            break

    # Detect Severity
    severity = 1
    if any(w in text_lower for w in SEVERITY_HIGH):
        severity = 3
    elif any(w in text_lower for w in SEVERITY_MED):
        severity = 2

    # Heuristic confidence
    confidence = 0.7 if disaster_type != "other" else 0.4

    # Simple Action
    actions = {
        "flood": "Evacuate to higher ground immediately.",
        "fire": "Evacuate area and call fire brigade.",
        "landslide": "Move away from slopes/hillsides.",
        "hurricane": "Seek shelter indoors away from windows.",
        "medical": "Dispatch medical team immediately.",
        "other": "Assess situation and report status."
    }
    action = actions.get(disaster_type, "Investigate report.")

    return {
        "disaster_type": disaster_type,
        "severity": severity,
        "confidence": confidence,
        "suggested_action": action
    }

def classify_alert(text: str):
    api_key = os.getenv("OPENAI_API_KEY")

    # Optional LLM
    if api_key and len(api_key) > 10:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"""
            You are a disaster triage classifier. For the input message, output JSON:
            {{ "disaster_type": "string", "severity": int(1-3), "confidence": float(0-1), "suggested_action": "string (<=18 words)" }}
            Input: "{text}"
            Types: flood, fire, landslide, hurricane, medical, other.
            Consider urgency.
            """
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"LLM failed: {e}, falling back to rules.")

    return classify_text_rules(text)
