# File: agents/base_agent.py
"""
Base agent interface for the AI Design Suite.

All agents must inherit from BaseAgent and implement the run() method.
This provides a consistent interface for the orchestrator to work with.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import uuid
from datetime import datetime, timezone


class BaseAgent(ABC):
    """
    Abstract base class for all design agents.
    
    Provides common functionality including session management,
    shared resource access, and standardized input/output handling.
    """
    
    def __init__(self, session_id: str, meta: Dict[str, Any]):
        """
        Initialize the agent with session context and shared resources.
        
        Args:
            session_id: Unique identifier for the current session
            meta: Dictionary containing shared resources like:
                - llm_client: LLM client for AI interactions
                - asset_registry: Component and material database
                - supplier_db: Supplier and pricing information
                - cad_services: CAD conversion and analysis tools
                - config: Agent-specific configuration
        """
        self.session_id = session_id
        self.meta = meta
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        
        # Extract common services from meta
        self.llm_client = meta.get('llm_client')
        self.asset_registry = meta.get('asset_registry')
        self.supplier_db = meta.get('supplier_db')
        self.cad_services = meta.get('cad_services')
        self.config = meta.get('config', {})
        
    @abstractmethod
    async def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input and return a structured result.
        
        Args:
            input: Dictionary containing:
                - intent: The specific action requested (e.g., 'beam_design', 'site_layout')
                - params: Parameters specific to the intent
                - files: List of uploaded files (optional)
                - message: Natural language description (optional)
                - context: Additional context from previous interactions
                
        Returns:
            Dictionary with standardized structure:
                - status: 'success', 'error', or 'warning'
                - data: Main response data (varies by agent)
                - messages: Human-readable messages
                - files: Generated files (drawings, reports, etc.)
                - metadata: Additional information (execution time, etc.)
                - next_actions: Suggested follow-up actions
        """
        raise NotImplementedError("Subclasses must implement the run method")
    
    def get_session_context(self) -> Dict[str, Any]:
        """Get the current session context."""
        return {
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'created_at': self.created_at,
            'agent_type': self.__class__.__name__
        }
    
    def log_activity(self, message: str, level: str = 'info') -> None:
        """Log agent activity for audit and debugging."""
        # TODO: Implement proper logging to session storage
        print(f"[{level.upper()}] {self.__class__.__name__}: {message}")
    
    def validate_input(self, input: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that required fields are present in input.
        
        Args:
            input: Input dictionary to validate
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present
            
        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in input]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        return True
    
    def create_success_response(self, data: Any, message: str = "Operation completed successfully") -> Dict[str, Any]:
        """Create a standardized success response."""
        return {
            'status': 'success',
            'data': data,
            'messages': [message],
            'files': [],
            'metadata': {
                'agent_type': self.__class__.__name__,
                'session_id': self.session_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            'next_actions': []
        }
    
    def create_error_response(self, error: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            'status': 'error',
            'data': None,
            'messages': [error],
            'files': [],
            'metadata': {
                'agent_type': self.__class__.__name__,
                'session_id': self.session_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error_details': details
            },
            'next_actions': []
        }
    
    def create_warning_response(self, data: Any, warning: str) -> Dict[str, Any]:
        """Create a standardized warning response."""
        return {
            'status': 'warning',
            'data': data,
            'messages': [warning],
            'files': [],
            'metadata': {
                'agent_type': self.__class__.__name__,
                'session_id': self.session_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            'next_actions': []
        }


class ExecutorAgent(BaseAgent):
    """
    Base class for agents that can be used as workflow executors.
    
    Extends BaseAgent to work with Microsoft Agent Framework's
    workflow and executor patterns.
    """
    
    def __init__(self, session_id: str, meta: Dict[str, Any], executor_id: Optional[str] = None):
        super().__init__(session_id, meta)
        self.executor_id = executor_id or f"{self.__class__.__name__.lower()}_{self.agent_id[:8]}"
    
    async def handle_workflow_input(self, input: Any, context: Any) -> Any:
        """
        Handle input from workflow executor context.
        
        This method adapts the agent's run() method to work with
        Microsoft Agent Framework workflow patterns.
        """
        # Convert workflow input to agent input format
        if isinstance(input, dict):
            agent_input: Dict[str, Any] = input
        else:
            # Handle string or other input types
            agent_input = {'message': str(input), 'intent': 'general'}
        
        # Run the agent
        result = await self.run(agent_input)
        
        # Return data in format expected by workflow
        return result['data'] if result['status'] == 'success' else result