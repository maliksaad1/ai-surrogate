import asyncio
import os
import sys
from app.services.mcp_service import mcp_service

# Mock environment variables for testing
os.environ["GMAIL_ADDRESS"] = "test@example.com"
os.environ["GMAIL_APP_PASSWORD"] = "test_password"

async def test_mcp_integration():
    print("Initializing MCP Service...")
    await mcp_service.initialize()
    
    print("\nListing Tools:")
    tools = await mcp_service.list_tools()
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    print("\nTesting 'send_email' tool (simulated)...")
    try:
        # Note: This will fail with actual Gmail auth unless valid creds are present,
        # but we expect it to at least try and fail with auth error or success if mocked
        result = await mcp_service.call_tool("send_email", {
            "to": "recipient@example.com",
            "subject": "MCP Test",
            "body": "Hello from MCP!"
        })
        print(f"Result: {result}")
    except Exception as e:
        print(f"Tool execution failed (expected if no creds): {e}")

    print("\nTesting 'list_calendar_events' tool...")
    try:
        result = await mcp_service.call_tool("list_calendar_events", {
            "days_ahead": 3
        })
        
        # Format result
        response_text = ""
        if hasattr(result, 'content') and result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    response_text += content.text
                else:
                    response_text += str(content)
        print(f"Result: {response_text}")
        
    except Exception as e:
        print(f"Tool execution failed: {e}")

    print("\nShutting down...")
    await mcp_service.shutdown()

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(test_mcp_integration())
