"""
Tool system for AI Surrogate - MCP-like tool calling framework
"""

from .base import BaseTool, ToolResult, ToolExecutionContext
from .registry import tool_registry

__all__ = ['BaseTool', 'ToolResult', 'ToolExecutionContext', 'tool_registry']
