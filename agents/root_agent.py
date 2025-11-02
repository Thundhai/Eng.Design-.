# File: agents/root_agent.py
"""
Root Agent - Main orchestrator for the AI Design Suite.

Routes requests to appropriate specialized agents and manages
session context, shared resources, and multi-agent workflows.
"""

from typing import Any, Dict, List, Optional
import asyncio
from datetime import datetime, timezone

from .base_agent import BaseAgent
from .design_copilot_agent import DesignCopilotAgent
from .civil_agent import CivilDesignAgent
from .structural_agent import StructuralDesignAgent
from .mechanical_agent import MechanicalDesignAgent
from .electrical_agent import ElectricalDesignAgent
from .interior_agent import InteriorDesignAgent
from .bom_agent import BOMAgent
from .compliance_agent import ComplianceAgent
from .drawing_qa_agent import DrawingQAAgent
from .sustainability_agent import SustainabilityAgent
from .generative_design_agent import GenerativeDesignAgent
from .planning_engineer_agent import PlanningEngineerAgent


class RootAgent(BaseAgent):
    """
    Main orchestrator that routes requests to specialized agents.
    
    Handles:
    - Intent classification and routing
    - Session management
    - Multi-agent coordination
    - Resource sharing
    - Response composition
    """
    
    def __init__(self, session_id: str, meta: Dict[str, Any]):
        super().__init__(session_id, meta)
        
        # Intent mapping to agent classes
        self.agent_mapping = {
            'general': DesignCopilotAgent,
            'chat': DesignCopilotAgent,
            'copilot': DesignCopilotAgent,
            
            'civil': CivilDesignAgent,
            'site': CivilDesignAgent,
            'earthwork': CivilDesignAgent,
            'drainage': CivilDesignAgent,
            'road': CivilDesignAgent,
            
            'structural': StructuralDesignAgent,
            'structure': StructuralDesignAgent,
            'beam': StructuralDesignAgent,
            'column': StructuralDesignAgent,
            'foundation': StructuralDesignAgent,
            'load': StructuralDesignAgent,
            'fea': StructuralDesignAgent,
            
            'mechanical': MechanicalDesignAgent,
            'assembly': MechanicalDesignAgent,
            'tolerance': MechanicalDesignAgent,
            'mechanism': MechanicalDesignAgent,
            
            'electrical': ElectricalDesignAgent,
            'electric': ElectricalDesignAgent,
            'wiring': ElectricalDesignAgent,
            'lighting': ElectricalDesignAgent,
            'power': ElectricalDesignAgent,
            'schematic': ElectricalDesignAgent,
            
            'interior': InteriorDesignAgent,
            'space': InteriorDesignAgent,
            'furniture': InteriorDesignAgent,
            'layout': InteriorDesignAgent,
            'finishes': InteriorDesignAgent,
            
            'bom': BOMAgent,
            'cost': BOMAgent,
            'pricing': BOMAgent,
            'procurement': BOMAgent,
            'materials': BOMAgent,
            
            'compliance': ComplianceAgent,
            'code': ComplianceAgent,
            'standard': ComplianceAgent,
            'regulation': ComplianceAgent,
            
            'qa': DrawingQAAgent,
            'quality': DrawingQAAgent,
            'review': DrawingQAAgent,
            'check': DrawingQAAgent,
            'clash': DrawingQAAgent,
            
            'sustainability': SustainabilityAgent,
            'green': SustainabilityAgent,
            'carbon': SustainabilityAgent,
            'lca': SustainabilityAgent,
            'environment': SustainabilityAgent,
            
            'generative': GenerativeDesignAgent,
            'optimize': GenerativeDesignAgent,
            'variation': GenerativeDesignAgent,
            'parametric': GenerativeDesignAgent,
            
            'planning': PlanningEngineerAgent,
            'schedule': PlanningEngineerAgent,
            'construction': PlanningEngineerAgent,
            'sequencing': PlanningEngineerAgent,
            'resource': PlanningEngineerAgent,
            'timeline': PlanningEngineerAgent,
            'coordination': PlanningEngineerAgent,
        }
        
        # Cache for instantiated agents
        self._agent_cache: Dict[str, BaseAgent] = {}
    
    async def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and route to appropriate agent(s).
        
        Args:
            input: Dictionary containing:
                - message: Natural language input
                - intent: Explicit agent type (optional)
                - files: Uploaded files (optional)
                - multi_agent: Boolean for multi-agent workflow
                - agents: List of specific agents to use
                
        Returns:
            Composed response from agent(s)
        """
        try:
            self.log_activity(f"Processing request: {input.get('message', 'No message')[:100]}")
            
            # Extract and classify intent
            intent = await self._classify_intent(input)
            
            # Check for automated workflow keywords
            message = input.get('message', '').lower()
            if any(keyword in message for keyword in ['complete', 'full', 'comprehensive', 'automated', 'end-to-end']):
                return await self._handle_automated_workflow(input)
            
            # Handle multi-agent workflows
            if input.get('multi_agent', False) or len(intent) > 1:
                return await self._handle_multi_agent_workflow(input, intent)
            
            # Single agent workflow
            agent_type = intent[0] if intent else 'general'
            agent = await self._get_agent(agent_type)
            
            # Add session context to input
            enhanced_input = self._enhance_input(input)
            
            # Execute agent
            result = await agent.run(enhanced_input)
            
            # Enhance response with routing metadata
            result['metadata']['routing'] = {
                'intent_classified': intent,
                'agent_used': agent_type,
                'route_confidence': 1.0 if len(intent) == 1 else 0.8
            }
            
            return result
            
        except Exception as e:
            self.log_activity(f"Error in root agent: {str(e)}", 'error')
            return self.create_error_response(f"System error: {str(e)}")
    
    async def _classify_intent(self, input: Dict[str, Any]) -> List[str]:
        """
        Classify the intent from input to determine which agent(s) to use.
        
        Uses a combination of explicit intent, keyword matching,
        and LLM-based classification for complex cases.
        """
        # Check for explicit intent
        if 'intent' in input and input['intent'] in self.agent_mapping:
            return [input['intent']]
        
        # Check for explicit agent list
        if 'agents' in input:
            return [agent for agent in input['agents'] if agent in self.agent_mapping]
        
        message = input.get('message', '').lower()
        
        # Simple keyword-based classification
        detected_intents = []
        for keyword, agent_type in self.agent_mapping.items():
            if keyword in message:
                agent_name = agent_type.__name__.replace('Agent', '').lower()
                if agent_name not in detected_intents:
                    detected_intents.append(agent_name)
        
        # Advanced LLM-based classification for ambiguous cases
        if not detected_intents and self.llm_client:
            llm_intent = await self._llm_classify_intent(message)
            if llm_intent:
                detected_intents.append(llm_intent)
        
        # Default to general/copilot if no specific intent detected
        return detected_intents if detected_intents else ['general']
    
    async def _llm_classify_intent(self, message: str) -> Optional[str]:
        """Use LLM to classify complex or ambiguous intents."""
        try:
            prompt = f"""
            Classify the following design engineering request into ONE of these categories:
            - civil: Site planning, earthworks, drainage, roads
            - structural: Buildings, beams, columns, loads, foundations
            - mechanical: Assemblies, mechanisms, tolerances, manufacturing
            - electrical: Circuits, wiring, lighting, power systems
            - interior: Space planning, furniture, finishes, layouts
            - bom: Costing, materials, procurement, bill of materials
            - compliance: Code checking, standards, regulations
            - qa: Quality control, drawing review, clash detection
            - sustainability: Environmental impact, carbon, LCA
            - generative: Optimization, parametric design, variations
            - general: General questions or multi-disciplinary
            
            Request: "{message}"
            
            Respond with only the category name (e.g., "structural"):
            """
            
            response = await self.llm_client.generate(prompt)
            classified = response.strip().lower()
            
            # Validate response
            valid_categories = ['civil', 'structural', 'mechanical', 'electrical', 
                             'interior', 'bom', 'compliance', 'qa', 'sustainability', 
                             'generative', 'general']
            
            return classified if classified in valid_categories else None
            
        except Exception as e:
            self.log_activity(f"LLM classification failed: {str(e)}", 'warning')
            return None
    
    async def _handle_multi_agent_workflow(self, input: Dict[str, Any], intents: List[str]) -> Dict[str, Any]:
        """
        Handle workflows that require multiple agents.
        
        Can run agents sequentially or in parallel depending on dependencies.
        """
        self.log_activity(f"Starting multi-agent workflow with intents: {intents}")
        
        # Determine execution strategy
        parallel_agents = ['bom', 'compliance', 'qa', 'sustainability']
        sequential_agents = ['civil', 'structural', 'mechanical', 'electrical', 'interior']
        
        # Separate parallel and sequential agents
        parallel_tasks = [intent for intent in intents if intent in parallel_agents]
        sequential_tasks = [intent for intent in intents if intent in sequential_agents]
        
        results = []
        enhanced_input = self._enhance_input(input)
        
        # Run sequential agents first (they may produce data for parallel agents)
        for intent in sequential_tasks:
            agent = await self._get_agent(intent)
            result = await agent.run(enhanced_input)
            results.append(result)
            
            # Update input with previous results for context
            enhanced_input['context'] = enhanced_input.get('context', {})
            enhanced_input['context'][intent] = result['data']
        
        # Run parallel agents concurrently
        if parallel_tasks:
            parallel_results = await asyncio.gather(*[
                self._run_agent_with_context(intent, enhanced_input)
                for intent in parallel_tasks
            ])
            results.extend(parallel_results)
        
        # Compose final response
        return self._compose_multi_agent_response(results, intents)
    
    async def _handle_automated_workflow(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle automated workflow with intelligent agent coordination.
        """
        self.log_activity("Starting automated workflow")
        
        try:
            # Create automated workflow agent
            from .automated_workflow_agent import AutomatedWorkflowAgent
            workflow_agent = AutomatedWorkflowAgent(self.session_id, self.meta)
            
            # Execute automated workflow
            result = await workflow_agent.run(input)
            
            # Enhance result with root agent metadata
            if result.get('status') == 'success':
                result['metadata'] = {
                    'workflow_type': 'automated',
                    'orchestrated_by': 'root_agent',
                    'session_id': self.session_id,
                    **result.get('metadata', {})
                }
            
            return result
            
        except ImportError:
            self.log_activity("AutomatedWorkflowAgent not available, falling back to basic multi-agent", 'warning')
            # Fall back to basic multi-agent workflow
            detected_intents = await self._detect_required_agents(input.get('message', ''))
            return await self._handle_multi_agent_workflow(input, detected_intents)
            
        except Exception as e:
            self.log_activity(f"Automated workflow failed: {str(e)}", 'error')
            return self.create_error_response(f"Automated workflow failed: {str(e)}")
    
    async def _detect_required_agents(self, message: str) -> List[str]:
        """
        Detect which agents are needed based on message content.
        """
        message_lower = message.lower()
        required_agents = []
        
        # Analyze message for agent requirements
        if any(word in message_lower for word in ['building', 'structure', 'beam', 'column', 'foundation']):
            required_agents.extend(['civil', 'structural', 'bom', 'compliance'])
            
        if any(word in message_lower for word in ['complete', 'full', 'comprehensive', 'entire']):
            required_agents.extend(['structural', 'mechanical', 'electrical', 'interior', 'bom', 'compliance', 'qa'])
            
        if any(word in message_lower for word in ['cost', 'budget', 'estimate', 'pricing']):
            if 'bom' not in required_agents:
                required_agents.append('bom')
                
        if any(word in message_lower for word in ['optimize', 'improve', 'alternative', 'variation']):
            required_agents.append('generative')
            
        if any(word in message_lower for word in ['sustainable', 'green', 'carbon', 'environmental']):
            required_agents.append('sustainability')
        
        # Default to structural + BOM if nothing specific detected
        if not required_agents:
            required_agents = ['structural', 'bom']
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(required_agents))
    
    async def _run_agent_with_context(self, intent: str, input: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to run an agent with enhanced context."""
        agent = await self._get_agent(intent)
        return await agent.run(input)
    
    def _compose_multi_agent_response(self, results: List[Dict[str, Any]], intents: List[str]) -> Dict[str, Any]:
        """Compose multiple agent results into a unified response."""
        # Aggregate all data
        combined_data = {}
        all_messages = []
        all_files = []
        all_next_actions = []
        
        # Determine overall status
        has_errors = any(r['status'] == 'error' for r in results)
        has_warnings = any(r['status'] == 'warning' for r in results)
        
        status = 'error' if has_errors else ('warning' if has_warnings else 'success')
        
        for i, result in enumerate(results):
            agent_name = intents[i] if i < len(intents) else f"agent_{i}"
            combined_data[agent_name] = result['data']
            
            # Prefix messages with agent name
            agent_messages = [f"[{agent_name.upper()}] {msg}" for msg in result['messages']]
            all_messages.extend(agent_messages)
            
            all_files.extend(result.get('files', []))
            all_next_actions.extend(result.get('next_actions', []))
        
        return {
            'status': status,
            'data': combined_data,
            'messages': all_messages,
            'files': all_files,
            'metadata': {
                'agent_type': 'RootAgent',
                'session_id': self.session_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'workflow_type': 'multi_agent',
                'agents_used': intents,
                'execution_summary': f"Executed {len(results)} agents successfully"
            },
            'next_actions': all_next_actions
        }
    
    async def _get_agent(self, agent_type: str) -> BaseAgent:
        """Get or create an agent instance."""
        if agent_type in self._agent_cache:
            return self._agent_cache[agent_type]
        
        # Get agent class from mapping
        agent_class = self.agent_mapping.get(agent_type)
        if not agent_class:
            # Try to find by partial match
            for key, cls in self.agent_mapping.items():
                if agent_type.startswith(key) or key.startswith(agent_type):
                    agent_class = cls
                    break
        
        if not agent_class:
            # Default to DesignCopilotAgent for unknown types
            agent_class = DesignCopilotAgent
        
        # Create and cache agent
        agent = agent_class(self.session_id, self.meta)
        self._agent_cache[agent_type] = agent
        
        return agent
    
    def _enhance_input(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Add session context and metadata to input."""
        enhanced = input.copy()
        enhanced['session_context'] = self.get_session_context()
        enhanced['timestamp'] = datetime.now(timezone.utc).isoformat()
        return enhanced
    
    def get_available_agents(self) -> Dict[str, str]:
        """Get list of available agents and their descriptions."""
        return {
            'civil': 'Site planning, earthworks, drainage, road design',
            'structural': 'Building structures, beams, columns, foundations, load analysis',
            'mechanical': 'Assemblies, mechanisms, tolerances, manufacturing design',
            'electrical': 'Circuits, wiring, lighting, power distribution, schematics',
            'interior': 'Space planning, furniture layouts, finishes, materials',
            'bom': 'Bill of materials, costing, procurement, supplier management',
            'compliance': 'Code compliance, standards checking, regulations',
            'qa': 'Quality assurance, drawing review, clash detection',
            'sustainability': 'Environmental impact, carbon footprint, LCA analysis',
            'generative': 'Parametric design, optimization, design variations',
            'general': 'General design questions and multi-disciplinary coordination'
        }