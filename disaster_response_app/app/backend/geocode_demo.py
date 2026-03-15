# Simple demo geocoding for Jamaica locations
# In production, use Google Maps API or OpenStreetMap Nominatim

LOCATIONS = {
    "kingston": (17.9712, -76.7928),
    "st. andrew": (18.0059, -76.7797),
    "half way tree": (18.0123, -76.7983),
    "new kingston": (18.0075, -76.7830),
    "papine": (18.0246, -76.7369),
    "red hills": (18.0772, -76.8406),
    "mountain view ave": (17.9890, -76.7650),
    "marcus garvey drive": (17.9650, -76.8100),
    "portmore": (17.9702, -76.8688),
    "harbour view": (17.9486, -76.7336)
}

def geocode_location(name: str):
    if not name:
        return None, None
    name_lower = name.lower().strip()
    # Fuzzy match or direct lookup
    for key, coords in LOCATIONS.items():
        if key in name_lower or name_lower in key:
            return coords
    # Default fallback (Kingston center) if unknown, for demo purposes
    # returning None in real app, but for demo we want points on map
    return 17.9712, -76.7928
