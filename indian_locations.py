"""
Indian cities with coordinates for astronomy calculations
"""

INDIAN_CITIES = {
    # Major metros
    "delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi", "timezone": "Asia/Kolkata"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra", "timezone": "Asia/Kolkata"},
    "bangalore": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka", "timezone": "Asia/Kolkata"},
    "kolkata": {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal", "timezone": "Asia/Kolkata"},
    "chennai": {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu", "timezone": "Asia/Kolkata"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana", "timezone": "Asia/Kolkata"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra", "timezone": "Asia/Kolkata"},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat", "timezone": "Asia/Kolkata"},
    
    # Popular stargazing locations
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "state": "Rajasthan", "timezone": "Asia/Kolkata"},
    "udaipur": {"lat": 24.5854, "lon": 73.7125, "state": "Rajasthan", "timezone": "Asia/Kolkata"},
    "manali": {"lat": 32.2432, "lon": 77.1892, "state": "Himachal Pradesh", "timezone": "Asia/Kolkata"},
    "rishikesh": {"lat": 30.0869, "lon": 78.2676, "state": "Uttarakhand", "timezone": "Asia/Kolkata"},
    "ooty": {"lat": 11.4064, "lon": 76.6932, "state": "Tamil Nadu", "timezone": "Asia/Kolkata"},
    "goa": {"lat": 15.2993, "lon": 74.1240, "state": "Goa", "timezone": "Asia/Kolkata"},
    "darjeeling": {"lat": 27.0410, "lon": 88.2663, "state": "West Bengal", "timezone": "Asia/Kolkata"},
    "shimla": {"lat": 31.1048, "lon": 77.1734, "state": "Himachal Pradesh", "timezone": "Asia/Kolkata"},
    "coorg": {"lat": 12.3375, "lon": 75.8069, "state": "Karnataka", "timezone": "Asia/Kolkata"},
    "mount_abu": {"lat": 24.5925, "lon": 72.7156, "state": "Rajasthan", "timezone": "Asia/Kolkata"},
    
    # State capitals
    "lucknow": {"lat": 28.5355, "lon": 77.3910, "state": "Uttar Pradesh", "timezone": "Asia/Kolkata"},
    "bhopal": {"lat": 23.2599, "lon": 77.4126, "state": "Madhya Pradesh", "timezone": "Asia/Kolkata"},
    "chandigarh": {"lat": 30.7333, "lon": 76.7794, "state": "Chandigarh", "timezone": "Asia/Kolkata"},
    "thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366, "state": "Kerala", "timezone": "Asia/Kolkata"},
}

def get_city_info(city_name: str):
    """Get city information by name"""
    city_key = city_name.lower().replace(" ", "_")
    return INDIAN_CITIES.get(city_key)

def find_nearby_cities(lat: float, lon: float, radius_km: float = 100):
    """Find cities within radius"""
    import math
    
    nearby = []
    for city, info in INDIAN_CITIES.items():
        # Calculate distance using Haversine formula
        lat1, lon1 = math.radians(lat), math.radians(lon)
        lat2, lon2 = math.radians(info['lat']), math.radians(info['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = 6371 * c  # Earth radius in km
        
        if distance <= radius_km:
            nearby.append((city, info, distance))
    
    return sorted(nearby, key=lambda x: x[12])
