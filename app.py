import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Test if loading worked
api_key = os.getenv("OPENAI_API_KEY")
print(f"✅ API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"✅ API Key starts with: {api_key[:10]}...")

import uvicorn
from mcp_server import mcp

# Get the pure MCP app
app = mcp.http_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Astro-Weather server on port {port}")
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=port,
            reload=True,  
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
