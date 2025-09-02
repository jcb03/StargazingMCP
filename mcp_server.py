import os
import base64
from io import BytesIO
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastmcp import FastMCP
from pydantic import BaseModel
from PIL import Image
from openai import OpenAI

from auth import verify_bearer_token, get_my_number
from astro_service import AstronomyService
from weather_service import IndianWeatherService
from indian_locations import get_city_info, INDIAN_CITIES

class LocationRequest(BaseModel):
    city: str
    state: Optional[str] = ""
    date: Optional[str] = None

class StargazingRequest(BaseModel):
    city: str
    state: Optional[str] = ""
    celestial_object: Optional[str] = "general"

# Initialize FastMCP
mcp = FastMCP("Astro-Weather Stargazing Guide")

# Initialize services
astro_service = AstronomyService()
weather_service = IndianWeatherService()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🛠️ HELPER FUNCTIONS (Fixed - removed 'self' references)
def format_viewing_times(viewing_times: List[Dict]) -> str:
    """Format viewing times for display"""
    if not viewing_times:
        return "• No specific viewing times available"
    
    formatted = ""
    for time_period in viewing_times:
        formatted += f"• **{time_period.get('period', 'Evening')}**: {time_period.get('start_time', 'N/A')} - {time_period.get('end_time', 'N/A')}\n"
        formatted += f"  Quality: {time_period.get('quality', 'Good')} - {time_period.get('description', '')}\n"
    
    return formatted

def format_tips(tips: List[str]) -> str:
    """Format tips for display"""
    if not tips:
        return "• Check weather conditions before heading out"
    
    return "\n".join([f"• {tip}" for tip in tips[:5]])

def format_events(events: List[Dict]) -> str:
    """Format celestial events for display"""
    if not events:
        return "• No specific events in database for this period"
    
    formatted = ""
    for event in events[:5]:
        formatted += f"• **{event.get('date', 'TBD')}** at {event.get('time', 'TBD')}: {event.get('event', 'Unknown Event')}\n"
        formatted += f"  {event.get('description', '')}\n"
    
    return formatted

# 🔑 REQUIRED PUCH AI TOOLS
@mcp.tool()
async def validate() -> str:
    """Validation tool required by Puch"""
    return get_my_number()

@mcp.tool()
async def about() -> Dict[str, str]:
    """About tool required by Puch AI - returns server metadata"""
    return {
        "name": "Astro-Weather Stargazing Guide",
        "description": "AI-powered stargazing assistant for India. Combines real-time weather data with astronomical events to provide optimal stargazing recommendations for Indian locations. Features celestial event tracking, weather analysis, and personalized viewing suggestions."
    }

# 🌟 MAIN STARGAZING TOOLS
@mcp.tool()
async def get_stargazing_forecast(
    city: str,
    state: str = "",
    days_ahead: int = 3
) -> str:
    """
    Get comprehensive stargazing forecast for Indian cities combining weather and astronomy data
    """
    try:
        # Get city coordinates
        city_info = get_city_info(city)
        if not city_info:
            return f"❌ City '{city}' not found in Indian locations database. Try: {', '.join(list(INDIAN_CITIES.keys())[:10])}"
        
        lat, lon = city_info['lat'], city_info['lon']
        full_location = f"{city.title()}, {city_info['state']}"
        
        # Get weather data
        weather_data = await weather_service.get_weather_data(city, state or city_info['state'])
        weather_assessment = weather_service.get_stargazing_weather_assessment(weather_data)
        
        # Get astronomy data
        sun_moon_data = await astro_service.get_sun_moon_data(lat, lon)
        celestial_events = await astro_service.get_celestial_events(lat, lon, days_ahead)
        viewing_times = await astro_service.get_best_viewing_times(sun_moon_data, weather_data)
        
        # Generate AI analysis
        prompt = f"""
        Provide a comprehensive stargazing forecast for {full_location}, India.
        
        Current conditions:
        - Weather: {weather_data.get('current', {})}
        - Weather assessment: {weather_assessment}
        - Astronomy: {sun_moon_data.get('astronomy', {})}
        - Viewing times: {viewing_times}
        - Upcoming events: {celestial_events}
        
        Create a detailed stargazing guide including:
        1. Tonight's viewing conditions and recommendations
        2. Best viewing times with explanations
        3. What celestial objects to observe
        4. Weather impact analysis
        5. Tips for this specific location in India
        6. Upcoming celestial events to plan for
        
        Make it engaging and educational for Indian stargazers.
        Include both Hindi and English terms where appropriate.
        """
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200
        )
        
        # FIXED: Access response correctly
        ai_analysis = response.choices[0].message.content
        
        # Format final response
        astronomy = sun_moon_data.get('astronomy', {})
        current_weather = weather_data.get('current', {})
        
        return f"""
🌟 **Stargazing Forecast for {full_location}**

**📍 Location Details:**
• Coordinates: {lat:.4f}°N, {lon:.4f}°E
• Timezone: {city_info.get('timezone', 'Asia/Kolkata')}
• Date: {astronomy.get('date', datetime.now().strftime('%Y-%m-%d'))}

**🌤️ Current Weather Conditions:**
• Temperature: {current_weather.get('temperature', 'N/A')}°C
• Humidity: {current_weather.get('humidity', 'N/A')}%
• Cloud Cover: {current_weather.get('clouds', 'N/A')}%
• Visibility: {current_weather.get('visibility', 'N/A')}km
• Weather: {current_weather.get('weather', 'N/A')}

**⭐ Stargazing Assessment:**
{weather_assessment.get('emoji', '🌟')} **{weather_assessment.get('rating', 'Good')}** 
Score: {weather_assessment.get('score', 75)}/100

{weather_assessment.get('recommendation', 'Good conditions for stargazing!')}

**🌅 Sun & Moon Times:**
• Sunrise: {astronomy.get('sunrise', 'N/A')} IST
• Sunset: {astronomy.get('sunset', 'N/A')} IST
• Moonrise: {astronomy.get('moonrise', 'N/A')} IST
• Moonset: {astronomy.get('moonset', 'N/A')} IST
• Moon Phase: {astronomy.get('moon_phase', 'N/A')}
• Moon Illumination: {astronomy.get('moon_illumination_percentage', 'N/A')}%

**🔭 AI Stargazing Analysis:**
{ai_analysis}

**📅 Best Viewing Times:**
{format_viewing_times(viewing_times.get('viewing_times', []))}

**🎯 Viewing Tips:**
{format_tips(viewing_times.get('tips', []))}

⏰ **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M IST')}
🇮🇳 **Built for Indian stargazers**
"""
        
    except Exception as e:
        return f"❌ Error generating stargazing forecast: {str(e)}"

@mcp.tool()
async def find_celestial_object(
    city: str,
    celestial_object: str,
    state: str = ""
) -> str:
    """
    Find when and where to observe specific celestial objects from Indian locations
    """
    try:
        # Get city coordinates
        city_info = get_city_info(city)
        if not city_info:
            return f"❌ City '{city}' not found. Available cities: {', '.join(list(INDIAN_CITIES.keys())[:10])}"
        
        lat, lon = city_info['lat'], city_info['lon']
        full_location = f"{city.title()}, {city_info['state']}"
        
        # Get current astronomy data
        sun_moon_data = await astro_service.get_sun_moon_data(lat, lon)
        planetary_data = await astro_service.get_planetary_positions()
        
        # Generate AI analysis for specific object
        prompt = f"""
        Provide detailed observation guide for {celestial_object} from {full_location}, India.
        
        Location details:
        - Coordinates: {lat:.4f}°N, {lon:.4f}°E
        - Current astronomy data: {sun_moon_data.get('astronomy', {})}
        - Planetary positions: {planetary_data}
        
        For the celestial object "{celestial_object}", provide:
        1. Current visibility status (visible/not visible tonight)
        2. Best viewing times and direction (compass direction)
        3. Altitude and azimuth information
        4. What to look for (appearance, brightness, etc.)
        5. Equipment recommendations (naked eye, binoculars, telescope)
        6. Photography tips if applicable
        7. Upcoming best viewing dates
        8. Cultural/mythological significance in Indian astronomy if relevant
        
        Make it practical for Indian observers with local references.
        Include Hindi names of constellations where applicable.
        """
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        # FIXED: Access response correctly
        ai_analysis = response.choices[0].message.content
        
        return f"""
🔭 **Celestial Object Guide: {celestial_object.title()}**

📍 **Observing from:** {full_location}
🗓️ **Date:** {datetime.now().strftime('%Y-%m-%d')}

{ai_analysis}

**🌙 Current Moon Conditions:**
• Phase: {sun_moon_data.get('astronomy', {}).get('moon_phase', 'N/A')}
• Illumination: {sun_moon_data.get('astronomy', {}).get('moon_illumination_percentage', 'N/A')}%
• Impact on viewing: {"🌚 Dark sky - excellent for faint objects" if float(sun_moon_data.get('astronomy', {}).get('moon_illumination_percentage', '50').replace('%', '')) < 30 else "🌕 Bright moon - focus on planets and bright objects"}

**📱 Recommended Apps:**
• SkySafari or Star Walk for object identification
• ISS Detector for satellite passes
• Sun Surveyor for planning observations

Built with ❤️ for Indian stargazers 🇮🇳
"""
        
    except Exception as e:
        return f"❌ Error finding celestial object: {str(e)}"

@mcp.tool()
async def get_upcoming_events(
    city: str,
    days_ahead: int = 14,
    state: str = ""
) -> str:
    """
    Get upcoming astronomical events and optimal viewing dates for Indian locations
    """
    try:
        # Get city coordinates
        city_info = get_city_info(city)
        if not city_info:
            return f"❌ City not found. Try: {', '.join(list(INDIAN_CITIES.keys())[:8])}"
        
        lat, lon = city_info['lat'], city_info['lon']
        full_location = f"{city.title()}, {city_info['state']}"
        
        # Get celestial events
        events_data = await astro_service.get_celestial_events(lat, lon, days_ahead)
        
        # Generate AI analysis
        prompt = f"""
        Create an astronomical events calendar for {full_location}, India for the next {days_ahead} days.
        
        Available events data: {events_data}
        Location: {lat:.4f}°N, {lon:.4f}°E
        
        Provide:
        1. Upcoming astronomical events (eclipses, meteor showers, planetary alignments)
        2. Best viewing dates for planets (Jupiter, Saturn, Mars, Venus)
        3. Moon phases and their impact on stargazing
        4. International Space Station (ISS) passes
        5. Seasonal constellation highlights
        6. Special events like comet appearances
        7. Photography opportunities
        
        For each event, include:
        - Date and time in IST
        - Visibility from this Indian location
        - Viewing tips and equipment needed
        - Duration of the event
        
        Include cultural context where relevant (Indian astronomical traditions).
        """
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200
        )
        
        # FIXED: Access response correctly
        ai_calendar = response.choices[0].message.content
        
        return f"""
🗓️ **Astronomical Events Calendar**

📍 **Location:** {full_location}
📅 **Period:** Next {days_ahead} days from {datetime.now().strftime('%Y-%m-%d')}

{ai_calendar}

**🔗 Events from Database:**
{format_events(events_data.get('events', []))}

**🌟 Pro Tips for Indian Observers:**
• Best viewing is 1-2 hours after sunset and before sunrise
• Head to darker areas outside city limits for better visibility
• Use red light to preserve night vision
• Check local weather forecasts before planning trips

**📱 Useful Resources:**
• TimeAndDate.com for precise local times
• In-The-Sky.org for detailed event information
• NASA's eclipse website for eclipse paths

⏰ **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M IST')}
🇮🇳 **Tailored for India**
"""
        
    except Exception as e:
        return f"❌ Error getting upcoming events: {str(e)}"

@mcp.tool()
async def suggest_stargazing_locations(
    city: str,
    radius_km: int = 100,
    state: str = ""
) -> str:
    """
    Suggest best stargazing locations near Indian cities considering light pollution
    """
    try:
        # Get city info
        city_info = get_city_info(city)
        if not city_info:
            return f"❌ City not found in database"
        
        lat, lon = city_info['lat'], city_info['lon']
        
        # Generate AI recommendations for stargazing spots
        prompt = f"""
        Suggest the best stargazing locations within {radius_km}km of {city.title()}, {city_info['state']}, India.
        
        Base location: {lat:.4f}°N, {lon:.4f}°E
        
        Provide recommendations for:
        1. Dark sky locations with minimal light pollution
        2. Accessible spots for families and beginners
        3. Advanced locations for serious astronomers
        4. Hill stations or elevated areas nearby
        5. Lakes or open areas with clear horizons
        
        For each location, include:
        - Approximate distance from {city}
        - Accessibility (road conditions, permits needed)
        - Best features for stargazing
        - Accommodation options if overnight
        - Safety considerations
        - Local attractions to combine with stargazing
        
        Focus on real, accessible locations in India.
        Include practical travel information.
        """
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        # FIXED: Access response correctly
        ai_suggestions = response.choices[0].message.content
        
        # Find nearby cities from database
        from indian_locations import find_nearby_cities
        nearby_cities = find_nearby_cities(lat, lon, radius_km)
        
        nearby_info = ""
        for city_name, info, distance in nearby_cities[:5]:
            if distance > 10:  # Skip very close cities
                nearby_info += f"• {city_name.replace('_', ' ').title()}: {distance:.0f}km away\n"
        
        return f"""
🏔️ **Best Stargazing Locations near {city.title()}**

📍 **Search radius:** {radius_km}km from {city.title()}, {city_info['state']}

{ai_suggestions}

**🌃 Nearby Cities in Database:**
{nearby_info}

**🚗 General Travel Tips:**
• Travel during new moon phases for darkest skies
• Carry warm clothing - temperatures drop at night
• Bring red flashlight to preserve night vision
• Check local weather and road conditions
• Inform family/friends about your stargazing plans

**📱 Apps for Light Pollution:**
• Light Pollution Map (shows dark sky areas)
• Clear Outside (weather for astronomy)
• PhotoPills (planning tool for astrophotography)

**🏕️ Stargazing Etiquette:**
• Leave no trace - clean up after yourself
• Use minimal lighting to not disturb others
• Respect private property and local communities
• Follow park/reserve rules and timings

Built for Indian stargazers 🇮🇳 ⭐
"""
        
    except Exception as e:
        return f"❌ Error suggesting locations: {str(e)}"

@mcp.tool()
async def help() -> str:
    """Get help and see all available Astro-Weather tools"""
    return """
🌟 **Astro-Weather Stargazing Guide - India**

**मुख्य सुविधाएं (Main Features):**

🔭 **get_stargazing_forecast** - Complete stargazing forecast with weather + astronomy
🌟 **find_celestial_object** - Find when/where to observe planets, constellations, etc.
📅 **get_upcoming_events** - Astronomical events calendar for your location  
🏔️ **suggest_stargazing_locations** - Best dark sky spots near Indian cities

**भारतीय शहर (Supported Indian Cities):**
Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad, Jaipur, Udaipur, Manali, Rishikesh, Ooty, Goa, Darjeeling, Shimla, Coorg, Mount Abu

**उपयोग कैसे करें (How to Use):**
1. WhatsApp पर Puch AI से जुड़ें
2. "Delhi में आज रात stargazing कैसी रहेगी?" पूछें
3. "Jupiter कब दिखेगा Mumbai से?" जानें
4. "Bangalore के पास dark sky locations" खोजें

**Example Commands:**
- "Stargazing forecast for Delhi tonight"
- "When can I see Saturn from Bangalore?"
- "Upcoming meteor showers in Chennai"
- "Best stargazing spots near Jaipur"

**विशेषताएं (Features):**
✅ Real-time Indian weather data
✅ Astronomical calculations for India
✅ Light pollution considerations
✅ Hindi + English support
✅ Cultural astronomical references
✅ Photography tips

**🌌 Celestial Objects You Can Track:**
Planets (Jupiter, Saturn, Mars, Venus), Moon phases, Constellations, Meteor showers, International Space Station (ISS), Comets, Eclipses

🚀 Built for Indian stargazers with ❤️
🏆 Combining astronomy + meteorology for perfect stargazing
"""

# Export the mcp server
__all__ = ["mcp"]
