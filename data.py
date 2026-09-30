import math

def get_weather(lat, lon):
    """
    Returns estimated 72h rainfall (mm) and max gust speed (km/h) for landfall area.
    """
    rain72 = round(220.0 + (abs(lat) * 2.8), 1)
    gust = round(140.0 + (abs(lon) * 0.4), 1)
    return rain72, gust

def get_assets(lat, lon):
    """
    Generates key infrastructure assets near landfall coordinates.
    """
    return [
        {"name": "Substation Alpha (Grid)", "type": "Power Grid", "lat": lat + 0.02, "lon": lon - 0.01, "elev": 1.8},
        {"name": "District General Hospital", "type": "Medical Facility", "lat": lat - 0.01, "lon": lon + 0.02, "elev": 4.5},
        {"name": "National Highway 316", "type": "Arterial Transport", "lat": lat + 0.04, "lon": lon - 0.03, "elev": 1.2},
        {"name": "Coastal Water Treatment Plant", "type": "Water Utility", "lat": lat - 0.03, "lon": lon - 0.02, "elev": 0.9},
        {"name": "Regional Telecom Tower B", "type": "Communications", "lat": lat + 0.01, "lon": lon + 0.04, "elev": 6.5},
    ]

def get_elevation(assets):
    """
    Elevations are already mapped into assets.
    """
    pass