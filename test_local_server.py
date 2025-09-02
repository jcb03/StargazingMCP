import requests
import json
import time
import uuid

# Generate a session ID for testing
session_id = str(uuid.uuid4())

BASE_URL = "http://localhost:8000/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "mcp-session-id": session_id  # Added session header
}

def test_tools_list():
    """Test tools list endpoint"""
    print("🧪 Testing tools list...")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        tools = data.get("result", {}).get("tools", [])
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   🔧 {tool.get('name', 'unnamed')}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def test_validate():
    """Test validate tool"""
    print("\n🧪 Testing validate tool...")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "validate",
            "arguments": {}
        },
        "id": 2
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        result = data.get("result")
        if isinstance(result, dict) and "content" in result:
            content = result["content"][0]["text"]
            print(f"✅ Validate returned: {content}")
            return content == "918920560661"
        print(f"✅ Direct result: {result}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def test_stargazing_forecast():
    """Test stargazing forecast tool"""
    print("\n🧪 Testing stargazing forecast...")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_stargazing_forecast",
            "arguments": {
                "city": "delhi",
                "state": "delhi", 
                "days_ahead": 3
            }
        },
        "id": 3
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        result = data.get("result")
        if result:
            if isinstance(result, dict) and "content" in result:
                content = result["content"][0]["text"]
                print("✅ Stargazing forecast generated successfully!")
                print(f"📋 Preview: {content[:200]}...")
            else:
                print(f"✅ Direct result received: {str(result)[:200]}...")
            return True
        print("⚠️ Empty result received")
        return False
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def run_all_tests():
    """Run all local tests"""
    print("🚀 Starting AstroWeather MCP Server Tests")
    print("=" * 50)
    
    tests = [
        test_tools_list,
        test_validate,
        test_stargazing_forecast
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(1)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed >= 2:
        print("🎉 Core tests passed! Server is working!")
        if passed == len(tests):
            print("🌟 All tests passed! Ready for deployment!")
    else:
        print("⚠️ Some core tests failed. Check server logs.")

if __name__ == "__main__":
    run_all_tests()
