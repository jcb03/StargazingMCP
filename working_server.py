import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Test API key
api_key = os.getenv("OPENAI_API_KEY") 
print(f"✅ API Key loaded: {'Yes' if api_key else 'No'}")

try:
    from fastmcp import FastMCP
    from openai import OpenAI
    print("✅ FastMCP and OpenAI imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

try:
    # Import your services with error handling
    from auth import get_my_number
    from indian_locations import get_city_info, INDIAN_CITIES
    print("✅ Local modules imported successfully")
    
    # Try weather and astro services (optional)
    try:
        from weather_service import IndianWeatherService
        from astro_service import AstronomyService
        weather_service = IndianWeatherService()
        astro_service = AstronomyService()
        print("✅ Weather and Astronomy services imported")
    except ImportError as e:
        print(f"⚠️ Weather/Astro services not available: {e}")
        weather_service = None
        astro_service = None
    
except ImportError as e:
    print(f"❌ Local module import error: {e}")
    print("Creating minimal versions...")
    
    def get_my_number():
        return "918920560661"
    
    def get_city_info(city):
        cities = {"delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi"}}
        return cities.get(city.lower())
    
    INDIAN_CITIES = {"delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi"}}
    weather_service = None
    astro_service = None

# Initialize FastMCP with stateless mode
mcp = FastMCP("Astro-Weather Stargazing Guide", stateless_http=True)

# Initialize OpenAI client
client = OpenAI(api_key=api_key) if api_key else None

@mcp.tool()
async def validate() -> str:
    """Validation tool required by Puch"""
    return get_my_number()

@mcp.tool()
async def about() -> dict:
    """About tool required by Puch AI"""
    return {
        "name": "Astro-Weather Stargazing Guide",
        "description": "AI-powered stargazing assistant for India",
        "status": "Working with simplified features"
    }

@mcp.tool()
async def get_stargazing_forecast(city: str, state: str = "", days_ahead: int = 3) -> str:
    """Get stargazing forecast for Indian cities"""
    try:
        # Get city info
        city_info = get_city_info(city.lower())
        if not city_info:
            available = list(INDIAN_CITIES.keys())[:5]
            return f"❌ City '{city}' not found. Try: {', '.join(available)}"
        
        lat, lon = city_info['lat'], city_info['lon']
        location = f"{city.title()}, {city_info['state']}"
        
        # Simplified forecast (no external APIs for now)
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": f"Provide a simple stargazing forecast for {location}, India. Include tonight's viewing conditions, best times, and recommended celestial objects. Keep it under 300 words."
                    }],
                    max_tokens=400
                )
                
                ai_content = response.choices[0].message.content
                
                return f"""
🌟 **Stargazing Forecast for {location}**

📍 **Location:** {lat:.4f}°N, {lon:.4f}°E
📅 **Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

{ai_content}

⏰ **Updated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M IST')}
🇮🇳 **Built for Indian stargazers**
                """
                
            except Exception as e:
                return f"❌ OpenAI error: {str(e)}"
        else:
            return f"""
🌟 **Stargazing Forecast for {location}**

📍 **Location:** {lat:.4f}°N, {lon:.4f}°E  
📅 **Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

**🌤️ Tonight's Conditions:**
• Clear skies expected for stargazing
• Best viewing: 21:00 - 02:00 IST
• Recommended: Jupiter, Saturn, Moon

**🔭 What to Observe:**
• Planets: Look for bright Jupiter in the evening sky
• Constellations: Great time to spot Ursa Major (सप्तर्षि)
• Moon: Check current phase for optimal viewing

**💡 Tips:**
• Head away from city lights for best views
• Allow 20 minutes for eyes to adjust to darkness
• Use red flashlight to preserve night vision

⏰ **Updated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M IST')}
🇮🇳 **Built for Indian stargazers**
            """
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def help() -> str:
    """Get help for available tools"""
    return """
🌟 **Astro-Weather Stargazing Guide - India**

**Available Tools:**
🔭 get_stargazing_forecast - Stargazing forecast for Indian cities
✅ validate - Server validation  
ℹ️ about - About this server
❓ help - This help message

**Usage Examples:**
• get_stargazing_forecast(city="delhi")
• get_stargazing_forecast(city="mumbai", state="maharashtra")

**Supported Cities:**
Delhi, Mumbai, Bangalore, Chennai

🚀 Built for Indian stargazers with ❤️
    """

# Create app
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AstroWeather server...")
    uvicorn.run(
        "working_server:app",
        host="0.0.0.0",
        port=8000, 
        reload=True,
        log_level="info"
    )
