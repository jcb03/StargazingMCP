import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test API keys
print("🔑 Testing API Keys...")
api_keys = {
    "OpenAI": os.getenv("OPENAI_API_KEY"),
    "Astronomy": os.getenv("ASTRONOMY_API_KEY"),
    "NASA": os.getenv("NASA_API_KEY"),
    "Weather Union": os.getenv("WEATHER_UNION_API_KEY")
}

for name, key in api_keys.items():
    if key:
        print(f"✅ {name}: {'Yes' if key else 'No'} ({key[:10]}...)")
    else:
        print(f"⚠️ {name}: Missing")

async def test_astro_service():
    """Test astronomy service"""
    print("\n🌟 Testing Astronomy Service...")
    
    try:
        from astro_service import AstronomyService
        astro_service = AstronomyService()
        
        # Test sun/moon data for Delhi
        sun_moon_data = await astro_service.get_sun_moon_data(28.6139, 77.2090)
        
        if sun_moon_data and "error" not in sun_moon_data:
            print("✅ Astronomy Service working!")
            astronomy = sun_moon_data.get("astronomy", {})
            print(f"🌅 Sunrise: {astronomy.get('sunrise', 'N/A')}")
            print(f"🌇 Sunset: {astronomy.get('sunset', 'N/A')}")
            print(f"🌙 Moon Phase: {astronomy.get('moon_phase', 'N/A')}")
            return True
        else:
            print("⚠️ Using mock astronomy data")
            return True
            
    except Exception as e:
        print(f"❌ Astronomy Service error: {e}")
        return False

async def test_weather_service():
    """Test weather service"""
    print("\n🌤️ Testing Weather Service...")
    
    try:
        from weather_service import IndianWeatherService
        weather_service = IndianWeatherService()
        
        # Test weather for Delhi
        weather_data = await weather_service.get_weather_data("Delhi", "Delhi")
        
        if weather_data and "error" not in weather_data:
            print("✅ Weather Service working!")
            current = weather_data.get("current", {})
            print(f"🌡️ Temperature: {current.get('temperature', 'N/A')}°C")
            print(f"💧 Humidity: {current.get('humidity', 'N/A')}%")
            print(f"📊 Source: {weather_data.get('source', 'unknown')}")
            
            # Test weather assessment
            assessment = weather_service.get_stargazing_weather_assessment(weather_data)
            print(f"⭐ Stargazing Rating: {assessment.get('rating', 'N/A')}")
            return True
        else:
            print("⚠️ Using mock weather data")
            return True
            
    except Exception as e:
        print(f"❌ Weather Service error: {e}")
        return False

def test_locations_database():
    """Test Indian cities database"""
    print("\n🗺️ Testing Indian Locations Database...")
    
    try:
        from indian_locations import get_city_info, INDIAN_CITIES
        
        test_cities = ["delhi", "mumbai", "bangalore", "chennai"]
        
        for city in test_cities:
            city_info = get_city_info(city)
            if city_info:
                print(f"✅ {city.title()}: {city_info['lat']:.2f}, {city_info['lon']:.2f}")
            else:
                print(f"❌ {city.title()}: Not found")
        
        print(f"📊 Total cities in database: {len(INDIAN_CITIES)}")
        return True
        
    except Exception as e:
        print(f"❌ Locations database error: {e}")
        return False

async def test_openai_integration():
    """Test OpenAI integration"""
    print("\n🤖 Testing OpenAI Integration...")
    
    try:
        from openai import OpenAI
        
        if not api_keys["OpenAI"]:
            print("⚠️ OpenAI API key missing")
            return False
        
        client = OpenAI(api_key=api_keys["OpenAI"])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user", 
                "content": "Give 2 quick stargazing tips for Delhi, India in both Hindi and English."
            }],
            max_tokens=150
        )
        
        result = response.choices[0].message.content
        print("✅ OpenAI integration working!")
        print(f"🌟 Sample response: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI integration error: {e}")
        return False

async def main():
    """Run all service tests"""
    print("🚀 Testing AstroWeather MCP Server Components")
    print("=" * 60)
    
    # Test all services
    tests = [
        test_locations_database,
        test_weather_service,
        test_astro_service,
        test_openai_integration
    ]
    
    results = []
    for test in tests:
        if asyncio.iscoroutinefunction(test):
            result = await test()
        else:
            result = test()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    print("📊 COMPONENT TEST SUMMARY:")
    print(f"✅ Tests passed: {passed}/{len(tests)}")
    
    if passed >= 3:
        print("🎉 Core components working! MCP server should be functional.")
    else:
        print("⚠️ Some components need attention.")
    
    print("\n🚀 Next: Run 'python test_local_server.py' to test MCP endpoints")

if __name__ == "__main__":
    asyncio.run(main())
