import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from openai import OpenAI

# Load environment variables
load_dotenv()

# Test API key
api_key = os.getenv("OPENAI_API_KEY")
print(f"✅ API Key loaded: {'Yes' if api_key else 'No'}")

# Create minimal MCP server
mcp = FastMCP("Test Server", stateless_http=True)

# Add basic health route
@mcp.tool()
async def health() -> str:
    """Simple health check"""
    return "Server is running! 🚀"

@mcp.tool()  
async def validate() -> str:
    """Validation tool"""
    return "918920560661"

# Export app
app = mcp.http_app()

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting minimal test server...")
    uvicorn.run(
        "minimal_server:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
