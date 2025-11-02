"""
Tool registry for managing all available tools
"""

from typing import Dict, List, Optional, Any
from .base import BaseTool, ToolExecutionContext, ToolResult


class ToolRegistry:
    """
    Central registry for all tools in the system.
    Manages tool registration, discovery, and execution.
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_categories: Dict[str, List[str]] = {
            "communication": [],  # Gmail, SMS, etc.
            "scheduling": [],      # Calendar, reminders
            "booking": [],         # Flights, hotels, restaurants
            "information": [],     # Search, weather, news
            "productivity": [],    # Notes, tasks, documents
        }
    
    def register(self, tool: BaseTool, category: str = "productivity") -> None:
        """Register a tool in the registry"""
        if tool.name in self._tools:
            print(f"⚠️  Tool '{tool.name}' already registered, replacing...")
        
        self._tools[tool.name] = tool
        
        if category in self._tool_categories:
            if tool.name not in self._tool_categories[category]:
                self._tool_categories[category].append(tool.name)
        
        print(f"✓ Tool registered: {tool.name} (category: {category})")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a category"""
        tool_names = self._tool_categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self._tools.values())
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all tool schemas for AI function calling.
        Returns list of tool schemas compatible with Gemini function calling.
        """
        return [tool.get_tool_info() for tool in self._tools.values()]
    
    def get_tools_for_agent(self, agent_type: str) -> List[BaseTool]:
        """
        Get tools available for a specific agent type.
        This enables each agent to have its own set of specialized tools.
        """
        tool_mapping = {
            "chat": [],  # Chat agent doesn't use tools directly
            "emotion": [],
            "memory": [],
            "scheduler": ["create_calendar_event", "set_reminder", "check_availability"],
            "docs": ["search_information", "create_document"],
            "communication": ["send_email", "send_sms"],
            "booking": ["search_flights", "book_flight", "search_hotels", "book_hotel"]
        }
        
        tool_names = tool_mapping.get(agent_type, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found",
                message="Tool not found in registry"
            )
        
        return await tool.execute(parameters, context)
    
    def list_tools(self) -> List[str]:
        """Get names of all registered tools"""
        return list(self._tools.keys())
    
    def get_tool_count(self) -> int:
        """Get total number of registered tools"""
        return len(self._tools)
    
    def unregister(self, tool_name: str) -> bool:
        """Remove a tool from registry"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            
            # Remove from categories
            for category_tools in self._tool_categories.values():
                if tool_name in category_tools:
                    category_tools.remove(tool_name)
            
            print(f"✓ Tool unregistered: {tool_name}")
            return True
        
        return False


# Global tool registry instance
tool_registry = ToolRegistry()
