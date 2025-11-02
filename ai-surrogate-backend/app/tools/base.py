"""
Base tool infrastructure for AI Surrogate tool-calling system
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio


class ToolStatus(Enum):
    """Tool execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    CANCELLED = "cancelled"


@dataclass
class ToolExecutionContext:
    """Context for tool execution"""
    user_id: str
    thread_id: str
    message: str
    user_email: Optional[str] = None
    user_metadata: Dict[str, Any] = field(default_factory=dict)
    confirmation_callback: Optional[Callable] = None
    

@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str = ""
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message,
            "requires_confirmation": self.requires_confirmation,
            "confirmation_prompt": self.confirmation_prompt,
            "metadata": self.metadata,
            "execution_time": self.execution_time
        }


class BaseTool:
    """
    Base class for all tools in the AI Surrogate system.
    Similar to MCP (Model Context Protocol) tool interface.
    """
    
    def __init__(
        self, 
        name: str,
        description: str,
        requires_confirmation: bool = False,
        requires_auth: bool = False
    ):
        self.name = name
        self.description = description
        self.requires_confirmation = requires_confirmation
        self.requires_auth = requires_auth
        self.execution_log: List[Dict[str, Any]] = []
    
    async def execute(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """
        Execute the tool with given parameters
        
        Args:
            parameters: Tool-specific parameters
            context: Execution context with user info
            
        Returns:
            ToolResult with execution status and data
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate parameters
            validation = self.validate_parameters(parameters)
            if not validation["valid"]:
                return ToolResult(
                    success=False,
                    error=f"Invalid parameters: {validation['error']}",
                    message="Parameter validation failed"
                )
            
            # Check if confirmation is required
            if self.requires_confirmation and not parameters.get("confirmed", False):
                confirmation_prompt = self.get_confirmation_prompt(parameters, context)
                return ToolResult(
                    success=False,
                    requires_confirmation=True,
                    confirmation_prompt=confirmation_prompt,
                    message="User confirmation required"
                )
            
            # Execute the actual tool logic
            result = await self._execute_impl(parameters, context)
            
            # Log execution
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self._log_execution(parameters, result, context)
            
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_result = ToolResult(
                success=False,
                error=str(e),
                message=f"Tool execution failed: {str(e)}",
                execution_time=execution_time
            )
            self._log_execution(parameters, error_result, context)
            return error_result
    
    async def _execute_impl(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """
        Actual tool implementation - to be overridden by subclasses
        """
        raise NotImplementedError("Tool must implement _execute_impl method")
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool parameters
        
        Returns:
            dict with 'valid' (bool) and optional 'error' (str)
        """
        # Basic validation - subclasses should override for specific validation
        required_params = self.get_parameter_schema().get("required", [])
        
        for param in required_params:
            if param not in parameters:
                return {
                    "valid": False,
                    "error": f"Missing required parameter: {param}"
                }
        
        return {"valid": True}
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for tool parameters
        Used by AI to understand what parameters the tool needs
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def get_confirmation_prompt(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> str:
        """
        Generate confirmation prompt for user
        """
        return f"Are you sure you want to execute {self.name}?"
    
    def _log_execution(
        self, 
        parameters: Dict[str, Any],
        result: ToolResult,
        context: ToolExecutionContext
    ):
        """Log tool execution for debugging and analytics"""
        log_entry = {
            "tool": self.name,
            "user_id": context.user_id,
            "thread_id": context.thread_id,
            "parameters": parameters,
            "success": result.success,
            "execution_time": result.execution_time,
            "timestamp": datetime.utcnow().isoformat(),
            "error": result.error if not result.success else None
        }
        self.execution_log.append(log_entry)
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information for AI function calling"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameter_schema(),
            "requires_confirmation": self.requires_confirmation,
            "requires_auth": self.requires_auth
        }
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_log.copy()
