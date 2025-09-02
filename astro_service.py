import httpx
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

class AstronomyService:
    def __init__(self):
        self.astronomy_api_key = os.getenv("ASTRONOMY_API_KEY", "")
        self.nasa_api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        
        # API endpoints
        self.ipgeolocation_url = "https://api.ipgeolocation.io/v2/astronomy"
        self.nasa_apod_url = "https://api.nasa.gov/planetary/apod"
        self.nasa_neo_url = "https://api.nasa.gov/neo/rest/v1"
    
    async def get_sun_moon_data(self, lat: float, lon: float, date: str = None) -> Dict[str, Any]:
        """Get sun and moon data for location using IPGeolocation API"""
        try:
            params = {
                "lat": lat,
                "long": lon
            }
            
            if date:
                params["date"] = date
            
            if self.astronomy_api_key:
                params["apiKey"] = self.astronomy_api_key
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ipgeolocation_url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return self._get_mock_sun_moon_data()
                    
        except Exception as e:
            print(f"Astronomy API error: {e}")
            return self._get_mock_sun_moon_data()
    
    async def get_planetary_positions(self, date: str = None) -> Dict[str, Any]:
        """Get planetary positions from NASA API"""
        try:
            # Use NASA's API for planetary data
            today = datetime.now().strftime("%Y-%m-%d") if not date else date
            
            # This is a simplified example - NASA doesn't have a direct planetary position API
            # In reality, you'd use astronomical calculation libraries like PyEphem or Skyfield
            
            return {
                "date": today,
                "planets": {
                    "jupiter": {"visible": True, "constellation": "Taurus", "magnitude": -2.1},
                    "saturn": {"visible": True, "constellation": "Aquarius", "magnitude": 0.8},
                    "mars": {"visible": False, "constellation": "Gemini", "magnitude": 1.3},
                    "venus": {"visible": True, "constellation": "Leo", "magnitude": -4.2}
                }
            }
            
        except Exception as e:
            print(f"Planetary data error: {e}")
            return {"error": "Unable to fetch planetary data"}
    
    async def get_celestial_events(self, lat: float, lon: float, days_ahead: int = 7) -> Dict[str, Any]:
        """Get upcoming celestial events for location"""
        try:
            events = []
            base_date = datetime.now()
            
            # Mock celestial events - in production, integrate with astronomical calendars
            for i in range(days_ahead):
                date = base_date + timedelta(days=i)
                
                # Example events
                if date.day % 7 == 0:  # Mock: every 7th day has an event
                    events.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "time": "21:30",
                        "event": "Jupiter at opposition",
                        "description": "Jupiter will be closest to Earth and fully illuminated"
                    })
                
                if date.day % 14 == 0:  # Mock: meteor shower
                    events.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "time": "02:00",
                        "event": "Geminids Meteor Shower peak",
                        "description": "Best viewing after midnight, up to 60 meteors per hour"
                    })
            
            return {"events": events, "location": f"{lat}, {lon}"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_mock_sun_moon_data(self) -> Dict[str, Any]:
        """Mock astronomy data for testing"""
        return {
            "location": {"latitude": "28.6139", "longitude": "77.2090"},
            "astronomy": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "sunrise": "06:30",
                "sunset": "18:45",
                "moonrise": "20:15",
                "moonset": "08:30",
                "moon_phase": "WAXING_GIBBOUS",
                "moon_illumination_percentage": "75",
                "solar_noon": "12:37",
                "day_length": "12:15"
            }
        }
    
    async def get_best_viewing_times(self, sun_moon_data: Dict, weather_data: Dict) -> Dict[str, Any]:
        """Calculate best stargazing times based on astronomy and weather"""
        try:
            astronomy = sun_moon_data.get("astronomy", {})
            
            # Extract times
            sunset = astronomy.get("sunset", "18:45")
            moonset = astronomy.get("moonset", "23:30")
            sunrise = astronomy.get("sunrise", "06:30")
            
            # Check weather conditions
            current_weather = weather_data.get("current", {})
            cloud_cover = current_weather.get("clouds", 50)  # percentage
            visibility = current_weather.get("visibility", 10)  # km
            
            # Calculate viewing quality
            viewing_quality = "Excellent"
            if cloud_cover > 70:
                viewing_quality = "Poor"
            elif cloud_cover > 40:
                viewing_quality = "Fair"
            elif cloud_cover > 20:
                viewing_quality = "Good"
            
            # Best times (after sunset, before sunrise, considering moon)
            best_times = []
            
            # Evening viewing (after sunset)
            best_times.append({
                "period": "Evening",
                "start_time": sunset,
                "end_time": "23:00",
                "quality": viewing_quality,
                "description": "Best for planetary observation and bright deep-sky objects"
            })
            
            # Late night viewing (if moon sets early)
            if moonset and moonset < "02:00":
                best_times.append({
                    "period": "Late Night", 
                    "start_time": moonset,
                    "end_time": "04:00",
                    "quality": "Excellent" if cloud_cover < 30 else viewing_quality,
                    "description": "Dark skies perfect for faint galaxies and nebulae"
                })
            
            return {
                "viewing_times": best_times,
                "conditions": {
                    "cloud_cover": cloud_cover,
                    "visibility": visibility,
                    "overall_quality": viewing_quality
                },
                "tips": self._get_viewing_tips(viewing_quality, astronomy)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_viewing_tips(self, quality: str, astronomy: Dict) -> list:
        """Get viewing tips based on conditions"""
        tips = []
        
        if quality == "Excellent":
            tips.extend([
                "Perfect conditions for deep-sky photography",
                "Try observing faint galaxies like Andromeda",
                "Great time for meteor shower observation"
            ])
        elif quality == "Good":
            tips.extend([
                "Focus on bright planets and star clusters",
                "Double stars will be clearly visible",
                "Good for lunar observation"
            ])
        elif quality == "Fair":
            tips.extend([
                "Stick to bright objects like planets",
                "Moon and bright stars will be visible",
                "Wait for cloud breaks"
            ])
        else:  # Poor
            tips.extend([
                "Consider indoor astronomy activities",
                "Plan for better weather tomorrow",
                "Use astronomy apps to plan future sessions"
            ])
        
        # Moon-specific tips
        moon_illumination = astronomy.get("moon_illumination_percentage", "50")
        if float(moon_illumination.replace("%", "")) > 80:
            tips.append("Bright moon - excellent for lunar observation but challenging for deep-sky")
        elif float(moon_illumination.replace("%", "")) < 20:
            tips.append("New moon phase - perfect for observing faint deep-sky objects")
        
        return tips
