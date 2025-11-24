import asyncio
import os
import sys
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPService:
    """
    Service to manage connection to MCP servers and execute tools.
    """
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize connection to local MCP server"""
        if self.session:
            return

        # Path to the mcp_server.py script
        server_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp_server.py")
        
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script],
            env=os.environ.copy()
        )
        
        try:
            from contextlib import AsyncExitStack
            self.exit_stack = AsyncExitStack()
            
            read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            
            await self.session.initialize()
            print("MCP Service initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize MCP Service: {e}")
            if self.exit_stack:
                await self.exit_stack.aclose()
            self.session = None

    async def list_tools(self) -> List[Any]:
        """List available tools from MCP server"""
        if not self.session:
            await self.initialize()
            if not self.session:
                return []
        
        try:
            result = await self.session.list_tools()
            return result.tools
        except Exception as e:
            print(f"Error listing MCP tools: {e}")
            return []

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool"""
        if not self.session:
            await self.initialize()
            if not self.session:
                raise Exception("MCP Service not initialized")
        
        try:
            result = await self.session.call_tool(name, arguments)
            return result
        except Exception as e:
            print(f"Error calling MCP tool {name}: {e}")
            raise

    async def shutdown(self):
        """Cleanup resources"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.session = None

# Global instance
mcp_service = MCPService()
