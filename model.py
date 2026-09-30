import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula for distance in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def analyse(track, assets, rain72):
    """
    Calculates storm surge, distance to track, flood depth, and assigns asset risk.
    """
    landfall = track[-1]
    peak_kt = max(pt["kt"] for pt in track)
    
    # Parametric storm surge height in meters
    surge = round((peak_kt / 40.0) ** 1.8 * 0.45, 2)

    for asset in assets:
        dist_km = calculate_distance(landfall["lat"], landfall["lon"], asset["lat"], asset["lon"])
        asset["dTrack"] = round(dist_km, 1)
        
        # Calculate flood depth
        if surge > asset["elev"]:
            asset["depth"] = round(surge - asset["elev"], 2)
        else:
            asset["depth"] = 0.0

        # Estimate localized wind
        asset["wind"] = int(peak_kt * max(0.6, 1.0 - (dist_km / 100.0)))

        # Assign Risk Category
        if asset["depth"] > 1.0 or (asset["depth"] > 0.3 and asset["type"] in ["Power Grid", "Medical Facility"]):
            asset["risk"] = "HIGH"
        elif asset["depth"] > 0.0 or asset["wind"] > 85:
            asset["risk"] = "MED"
        else:
            asset["risk"] = "LOW"

    return surge