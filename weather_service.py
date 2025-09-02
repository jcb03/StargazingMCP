import httpx
import os
from typing import Dict, Any, Optional
from datetime import datetime

class IndianWeatherService:
    def __init__(self):
        self.weather_union_key = os.getenv("WEATHER_UNION_API_KEY", "")
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY", "")
        
        # API endpoints
        self.weather_union_url = "https://www.weatherunion.com/gw/weather/external/v0"
        self.openweather_url = "http://api.openweathermap.org/data/2.5"
    
    async def get_weather_data(self, city: str, state: str = "") -> Dict[str, Any]:
        """Get Indian weather data prioritizing Weather Union API"""
        try:
            # Try Weather Union first (best for India)
            weather_data = await self._get_weather_union_data(city, state)
            if weather_data and "error" not in weather_data:
                return weather_data
            
            # Fallback to OpenWeatherMap
            weather_data = await self._get_openweather_data(city, state)
            if weather_data and "error" not in weather_data:
                return weather_data
            
            # Final fallback to mock data
            return self._get_mock_weather_data(city)
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_weather_union_data(self, city: str, state: str) -> Dict[str, Any]:
        """Get weather from Weather Union API"""
        try:
            if not self.weather_union_key:
                return {"error": "Weather Union API key not configured"}
            
            headers = {"X-Zomato-API-Key": self.weather_union_key}
            
            # Weather Union requires location ID - simplified for this example
            location_id = self._get_weather_union_location_id(city, state)
            
            url = f"{self.weather_union_url}/get_weather_data"
            params = {"device_type": 1, "locality_id": location_id}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._format_weather_union_data(data, city, state)
                else:
                    return {"error": f"Weather Union API error: {response.status_code}"}
                    
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_openweather_data(self, city: str, state: str) -> Dict[str, Any]:
        """Get weather from OpenWeatherMap API"""
        try:
            if not self.openweather_key:
                return self._get_mock_weather_data(city)
            
            location = f"{city},{state},IN" if state else f"{city},IN"
            
            # Current weather
            current_url = f"{self.openweather_url}/weather"
            params = {"q": location, "appid": self.openweather_key, "units": "metric"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(current_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "source": "openweather",
                        "location": f"{city}, {state}",
                        "current": {
                            "temperature": data["main"]["temp"],
                            "humidity": data["main"]["humidity"],
                            "pressure": data["main"]["pressure"],
                            "weather": data["weather"]["description"],
                            "clouds": data.get("clouds", {}).get("all", 0),
                            "visibility": data.get("visibility", 10000) / 1000,  # Convert to km
                            "wind_speed": data.get("wind", {}).get("speed", 0)
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"OpenWeather API error: {response.status_code}"}
                    
        except Exception as e:
            return {"error": str(e)}
    
    def _get_weather_union_location_id(self, city: str, state: str) -> str:
        """Get Weather Union location ID - simplified mapping"""
        # Weather Union uses specific location IDs
        # This is a simplified mapping - in production, use their location API
        location_mapping = {
            "delhi": "ZWL005764",
            "mumbai": "ZWL001156", 
            "bangalore": "ZWL009586",
            "hyderabad": "ZWL002203",
            "chennai": "ZWL006475",
            "kolkata": "ZWL001113",
            "pune": "ZWL003552",
            "ahmedabad": "ZWL008752"
        }
        
        return location_mapping.get(city.lower(), "ZWL005764")  # Default to Delhi
    
    def _format_weather_union_data(self, data: Dict, city: str, state: str) -> Dict[str, Any]:
        """Format Weather Union response"""
        try:
            locality_weather = data.get("locality_weather_data", {})
            
            return {
                "source": "weather_union",
                "location": f"{city}, {state}",
                "current": {
                    "temperature": locality_weather.get("temperature"),
                    "humidity": locality_weather.get("humidity"),
                    "pressure": locality_weather.get("pressure"),
                    "weather": locality_weather.get("weather_description", "Clear"),
                    "clouds": locality_weather.get("cloud_cover", 0),
                    "visibility": locality_weather.get("visibility", 10),
                    "wind_speed": locality_weather.get("wind_speed", 0),
                    "rain": locality_weather.get("rain_intensity", 0)
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Weather Union data formatting error: {str(e)}"}
    
    def _get_mock_weather_data(self, city: str) -> Dict[str, Any]:
        """Mock weather data for testing"""
        return {
            "source": "mock",
            "location": f"{city}, India",
            "current": {
                "temperature": 25,
                "humidity": 65,
                "pressure": 1013,
                "weather": "Clear sky",
                "clouds": 20,
                "visibility": 10,
                "wind_speed": 5,
                "rain": 0
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stargazing_weather_assessment(self, weather_data: Dict) -> Dict[str, Any]:
        """Assess weather conditions for stargazing"""
        try:
            current = weather_data.get("current", {})
            
            clouds = current.get("clouds", 50)
            humidity = current.get("humidity", 60)
            wind_speed = current.get("wind_speed", 5)
            visibility = current.get("visibility", 10)
            rain = current.get("rain", 0)
            
            # Calculate stargazing score (0-100)
            score = 100
            
            # Cloud impact (most important)
            if clouds > 80:
                score -= 50
            elif clouds > 60:
                score -= 30
            elif clouds > 40:
                score -= 20
            elif clouds > 20:
                score -= 10
            
            # Humidity impact
            if humidity > 90:
                score -= 15
            elif humidity > 80:
                score -= 10
            elif humidity > 70:
                score -= 5
            
            # Rain impact
            if rain > 0:
                score -= 40
            
            # Visibility impact
            if visibility < 5:
                score -= 20
            elif visibility < 8:
                score -= 10
            
            # Wind impact (positive for clearing atmosphere)
            if wind_speed > 15:
                score -= 10
            elif 5 <= wind_speed <= 15:
                score += 5
            
            # Determine rating
            if score >= 80:
                rating = "Excellent"
                emoji = "🌟"
            elif score >= 65:
                rating = "Good"
                emoji = "⭐"
            elif score >= 45:
                rating = "Fair"
                emoji = "☁️"
            else:
                rating = "Poor"
                emoji = "🌧️"
            
            return {
                "score": max(0, min(100, score)),
                "rating": rating,
                "emoji": emoji,
                "factors": {
                    "cloud_cover": f"{clouds}%",
                    "humidity": f"{humidity}%", 
                    "visibility": f"{visibility}km",
                    "wind_speed": f"{wind_speed}km/h",
                    "precipitation": "Yes" if rain > 0 else "No"
                },
                "recommendation": self._get_weather_recommendation(score, current)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_weather_recommendation(self, score: int, weather: Dict) -> str:
        """Get weather-based recommendation"""
        if score >= 80:
            return "🌟 Perfect conditions for stargazing! Clear skies and excellent visibility."
        elif score >= 65:
            return "⭐ Good stargazing weather. Some clouds but should have clear patches."
        elif score >= 45:
            return "☁️ Fair conditions. Wait for cloud breaks or focus on bright objects."
        else:
            return "🌧️ Poor conditions for stargazing. Plan for another night."
