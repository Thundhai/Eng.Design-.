# File: agents/automated_workflow_agent.py
"""
Automated Workflow Agent

This agent manages fully automated multi-agent workflows where agents can
automatically call other agents based on task requirements and dependencies.
"""

import asyncio
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass
from .base_agent import BaseAgent


@dataclass
class TaskNode:
    """Represents a task in the workflow graph."""
    task_id: str
    agent_type: str
    description: str
    dependencies: List[str]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    priority: int = 1


@dataclass  
class WorkflowPlan:
    """Represents a complete workflow execution plan."""
    workflow_id: str
    tasks: List[TaskNode]
    execution_order: List[str]
    estimated_duration: float


class AutomatedWorkflowAgent(BaseAgent):
    """
    Manages fully automated multi-agent workflows with intelligent task planning,
    dependency resolution, and dynamic agent coordination.
    """
    
    def __init__(self, session_id: str, meta: Dict[str, Any]):
        super().__init__(session_id, meta)
        self.agent_description = "Automated workflow orchestration and management"
        
        # Workflow execution state
        self.active_workflows: Dict[str, WorkflowPlan] = {}
        self.completed_tasks: Dict[str, TaskNode] = {}
        
        # Agent capability definitions
        self.agent_capabilities = {
            'structural': {
                'inputs': ['loads', 'spans', 'materials', 'constraints'],
                'outputs': ['beam_design', 'column_design', 'foundation_specs', 'structural_analysis'],
                'dependencies': ['civil'],  # Structural often needs site info
                'triggers': ['bom', 'compliance'],  # Structural design triggers BOM and compliance
                'duration': 3.0
            },
            'civil': {
                'inputs': ['site_requirements', 'project_scope'],
                'outputs': ['site_analysis', 'foundation_requirements', 'utilities_plan'],
                'dependencies': [],  # Civil is often first
                'triggers': ['structural', 'sustainability'],
                'duration': 2.5
            },
            'mechanical': {
                'inputs': ['system_requirements', 'space_constraints', 'structural_design'],
                'outputs': ['mep_design', 'equipment_specs', 'system_layout'],
                'dependencies': ['structural', 'interior'],
                'triggers': ['electrical', 'bom'],
                'duration': 2.8
            },
            'electrical': {
                'inputs': ['power_requirements', 'mechanical_design', 'lighting_requirements'],
                'outputs': ['electrical_design', 'panel_schedules', 'cable_sizing'],
                'dependencies': ['mechanical', 'interior'],
                'triggers': ['bom', 'compliance'],
                'duration': 2.2
            },
            'interior': {
                'inputs': ['space_requirements', 'structural_constraints'],
                'outputs': ['space_plan', 'furniture_layout', 'finishes_schedule'],
                'dependencies': ['structural'],
                'triggers': ['mechanical', 'electrical'],
                'duration': 2.0
            },
            'bom': {
                'inputs': ['structural_design', 'mechanical_design', 'electrical_design'],
                'outputs': ['material_list', 'cost_estimate', 'procurement_plan'],
                'dependencies': ['structural', 'mechanical', 'electrical'],
                'triggers': ['compliance'],
                'duration': 1.5
            },
            'compliance': {
                'inputs': ['all_designs', 'building_codes'],
                'outputs': ['compliance_report', 'code_violations', 'recommendations'],
                'dependencies': ['structural', 'mechanical', 'electrical', 'bom'],
                'triggers': ['qa'],
                'duration': 2.0
            },
            'qa': {
                'inputs': ['all_designs', 'compliance_report'],
                'outputs': ['qa_report', 'clash_detection', 'quality_issues'],
                'dependencies': ['compliance'],
                'triggers': ['sustainability'],
                'duration': 1.8
            },
            'sustainability': {
                'inputs': ['material_list', 'energy_requirements', 'site_analysis'],
                'outputs': ['lca_analysis', 'carbon_footprint', 'sustainability_rating'],
                'dependencies': ['bom', 'mechanical'],
                'triggers': ['generative'],
                'duration': 2.5
            },
            'generative': {
                'inputs': ['design_constraints', 'optimization_goals'],
                'outputs': ['design_alternatives', 'parametric_models', 'optimization_results'],
                'dependencies': [],  # Can work independently
                'triggers': ['planning'],
                'duration': 3.5
            },
            'planning': {
                'inputs': ['all_designs', 'project_requirements', 'site_constraints', 'bom_data'],
                'outputs': ['project_schedule', 'construction_sequence', 'resource_plan', 'risk_assessment'],
                'dependencies': ['structural', 'civil', 'mechanical', 'electrical', 'bom', 'compliance'],
                'triggers': [],  # Planning is typically final comprehensive step
                'duration': 4.0
            }
        }
    
    async def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process automated workflow requests.
        
        Supports:
        - Automatic workflow planning from high-level requirements
        - Intelligent agent sequencing based on dependencies
        - Dynamic task creation based on intermediate results
        - Real-time workflow monitoring and adjustment
        """
        try:
            message = input.get('message', '')
            intent = input.get('intent', 'workflow_planning')
            
            self.log_activity(f"Processing automated workflow request: {intent}")
            
            # Route to specific handler
            if intent == 'create_workflow':
                return await self._create_automated_workflow(input)
            elif intent == 'execute_workflow':
                return await self._execute_workflow(input)
            elif intent == 'monitor_workflow':
                return await self._monitor_workflow(input)
            elif intent == 'optimize_workflow':
                return await self._optimize_workflow(input)
            else:
                return await self._plan_workflow_from_message(input)
                
        except Exception as e:
            self.log_activity(f"Error in automated workflow: {str(e)}", 'error')
            return self.create_error_response(f"Workflow automation failed: {str(e)}")
    
    async def _plan_workflow_from_message(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically plan a workflow from natural language requirements.
        """
        message = input.get('message', '')
        
        # Use LLM to analyze requirements and suggest workflow
        planning_prompt = f"""
        Analyze this engineering project request and determine what agents are needed:
        
        Request: "{message}"
        
        Available agents:
        - civil: Site planning, foundations, earthworks
        - structural: Buildings, beams, columns, loads
        - mechanical: HVAC, systems, equipment
        - electrical: Power, lighting, controls
        - interior: Space planning, layouts, finishes
        - bom: Materials, costing, procurement
        - compliance: Code checking, regulations
        - qa: Quality control, review, clash detection
        - sustainability: Environmental analysis, LCA
        - generative: Design optimization, alternatives
        
        Respond with JSON format:
        {{
            "primary_goal": "description",
            "required_agents": ["agent1", "agent2"],
            "project_type": "building/infrastructure/product",
            "complexity": "simple/medium/complex"
        }}
        """
        
        try:
            response = await self.llm_client.generate(planning_prompt)
            
            # Parse LLM response (simplified - in production would use proper JSON parsing)
            # For now, let's create a workflow based on common patterns
            workflow_plan = await self._create_intelligent_workflow_plan(message, input)
            
            # Execute the workflow automatically
            execution_result = await self._execute_intelligent_workflow(workflow_plan, input)
            
            return self.create_success_response(
                {
                    'workflow_plan': workflow_plan.__dict__,
                    'execution_result': execution_result,
                    'automated': True
                },
                f"Automated workflow completed successfully with {len(workflow_plan.tasks)} tasks"
            )
            
        except Exception as e:
            return self.create_error_response(f"Workflow planning failed: {str(e)}")
    
    async def _create_intelligent_workflow_plan(self, message: str, input: Dict[str, Any]) -> WorkflowPlan:
        """
        Create an intelligent workflow plan based on message analysis.
        """
        message_lower = message.lower()
        required_agents = []
        
        # Analyze message for agent requirements
        if any(word in message_lower for word in ['building', 'structure', 'beam', 'column', 'foundation']):
            required_agents.extend(['civil', 'structural', 'bom', 'compliance'])
            
        if any(word in message_lower for word in ['complete', 'full', 'comprehensive', 'entire']):
            required_agents.extend(['structural', 'mechanical', 'electrical', 'interior', 'bom', 'compliance', 'qa', 'planning'])
            
        if any(word in message_lower for word in ['cost', 'budget', 'estimate', 'pricing']):
            if 'bom' not in required_agents:
                required_agents.append('bom')
                
        if any(word in message_lower for word in ['optimize', 'improve', 'alternative', 'variation']):
            required_agents.append('generative')
            
        if any(word in message_lower for word in ['sustainable', 'green', 'carbon', 'environmental']):
            required_agents.append('sustainability')
            
        if any(word in message_lower for word in ['schedule', 'planning', 'construction', 'timeline', 'coordination', 'sequencing', 'resource']):
            required_agents.append('planning')
        
        # Default to structural + BOM if nothing specific detected
        if not required_agents:
            required_agents = ['structural', 'bom']
        
        # Remove duplicates and sort by dependencies
        required_agents = list(dict.fromkeys(required_agents))
        
        # Create tasks with intelligent dependencies
        tasks = []
        task_id_counter = 1
        
        for agent_type in required_agents:
            capability = self.agent_capabilities.get(agent_type, {})
            dependencies = []
            
            # Add dependencies that are also in required agents
            for dep in capability.get('dependencies', []):
                if dep in required_agents and dep != agent_type:
                    dependencies.append(f"task_{required_agents.index(dep) + 1}")
            
            task = TaskNode(
                task_id=f"task_{task_id_counter}",
                agent_type=agent_type,
                description=f"Execute {agent_type} agent for project requirements",
                dependencies=dependencies,
                inputs={'message': message, 'context': input.get('context', {})},
                outputs={},
                priority=1
            )
            tasks.append(task)
            task_id_counter += 1
        
        # Calculate execution order based on dependencies
        execution_order = self._calculate_execution_order(tasks)
        
        workflow_plan = WorkflowPlan(
            workflow_id=f"auto_workflow_{self.session_id}_{len(self.active_workflows) + 1}",
            tasks=tasks,
            execution_order=execution_order,
            estimated_duration=sum(self.agent_capabilities.get(task.agent_type, {}).get('duration', 2.0) for task in tasks)
        )
        
        return workflow_plan
    
    def _calculate_execution_order(self, tasks: List[TaskNode]) -> List[str]:
        """
        Calculate optimal execution order based on task dependencies.
        Uses topological sorting to resolve dependencies.
        """
        # Create dependency graph
        graph: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {}
        
        for task in tasks:
            graph[task.task_id] = task.dependencies.copy()
            in_degree[task.task_id] = len(task.dependencies)
        
        # Topological sort using Kahn's algorithm
        execution_order = []
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            # Update in-degrees of dependent tasks
            for task in tasks:
                if current in task.dependencies:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)
        
        return execution_order
    
    async def _execute_intelligent_workflow(self, workflow_plan: WorkflowPlan, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow with intelligent context passing between agents.
        """
        self.log_activity(f"Executing automated workflow: {workflow_plan.workflow_id}")
        
        results = {}
        context = input.get('context', {})
        
        # Execute tasks in dependency order
        for task_id in workflow_plan.execution_order:
            task = next((t for t in workflow_plan.tasks if t.task_id == task_id), None)
            if not task:
                continue
                
            self.log_activity(f"Executing task {task_id}: {task.agent_type}")
            
            # Wait for dependencies to complete
            for dep_id in task.dependencies:
                if dep_id not in results:
                    self.log_activity(f"Warning: Dependency {dep_id} not completed for {task_id}")
            
            # Prepare enhanced input with context from previous tasks
            enhanced_input = {
                'message': task.inputs.get('message', input.get('message', '')),
                'intent': task.agent_type,
                'context': context,
                'workflow_context': {
                    'workflow_id': workflow_plan.workflow_id,
                    'task_id': task_id,
                    'previous_results': results
                }
            }
            
            # Execute agent
            try:
                agent = await self._get_agent(task.agent_type)
                result = await agent.run(enhanced_input)
                
                # Store result and update context
                results[task_id] = result
                context[task.agent_type] = result.get('data', {})
                
                # Update task status
                task.status = "completed"
                task.outputs = result.get('data', {})
                
                self.log_activity(f"Task {task_id} completed successfully")
                
                # Check if this task should trigger additional agents
                await self._check_for_triggered_agents(task, result, workflow_plan, context)
                
            except Exception as e:
                self.log_activity(f"Task {task_id} failed: {str(e)}", 'error')
                task.status = "failed"
                results[task_id] = {'status': 'error', 'error': str(e)}
        
        # Compose final integrated response
        return await self._compose_integrated_response(results, workflow_plan, context)
    
    async def _check_for_triggered_agents(self, completed_task: TaskNode, result: Dict[str, Any], 
                                        workflow_plan: WorkflowPlan, context: Dict[str, Any]):
        """
        Check if completed task should trigger additional agents automatically.
        """
        capability = self.agent_capabilities.get(completed_task.agent_type, {})
        triggered_agents = capability.get('triggers', [])
        
        for triggered_agent in triggered_agents:
            # Check if triggered agent is not already in workflow
            existing_agents = [task.agent_type for task in workflow_plan.tasks]
            
            if triggered_agent not in existing_agents:
                # Determine if we should auto-add this agent based on results
                should_trigger = await self._should_trigger_agent(triggered_agent, result, context)
                
                if should_trigger:
                    self.log_activity(f"Auto-triggering {triggered_agent} agent based on {completed_task.agent_type} results")
                    
                    # Create and execute new task
                    new_task = TaskNode(
                        task_id=f"auto_task_{triggered_agent}_{len(workflow_plan.tasks) + 1}",
                        agent_type=triggered_agent,
                        description=f"Auto-triggered {triggered_agent} based on {completed_task.agent_type}",
                        dependencies=[completed_task.task_id],
                        inputs={'message': f"Process {triggered_agent} requirements", 'context': context},
                        outputs={}
                    )
                    
                    # Execute immediately (since dependencies are met)
                    try:
                        agent = await self._get_agent(triggered_agent)
                        enhanced_input = {
                            'message': new_task.inputs['message'],
                            'intent': triggered_agent,
                            'context': context
                        }
                        auto_result = await agent.run(enhanced_input)
                        
                        new_task.status = "completed"
                        new_task.outputs = auto_result.get('data', {})
                        workflow_plan.tasks.append(new_task)
                        
                        self.log_activity(f"Auto-triggered task {new_task.task_id} completed")
                        
                    except Exception as e:
                        self.log_activity(f"Auto-triggered task failed: {str(e)}", 'error')
    
    async def _should_trigger_agent(self, agent_type: str, previous_result: Dict[str, Any], 
                                  context: Dict[str, Any]) -> bool:
        """
        Determine if an agent should be automatically triggered based on previous results.
        """
        # Simple heuristics - in production this could use ML models
        
        if agent_type == 'bom' and previous_result.get('status') == 'success':
            # Always trigger BOM after successful design tasks
            return True
            
        if agent_type == 'compliance' and 'design' in str(previous_result).lower():
            # Trigger compliance after design tasks
            return True
            
        if agent_type == 'qa' and agent_type == 'compliance':
            # QA after compliance
            return True
            
        if agent_type == 'sustainability' and 'material' in str(previous_result).lower():
            # Sustainability after material-related tasks
            return True
        
        return False
    
    async def _compose_integrated_response(self, results: Dict[str, Any], 
                                         workflow_plan: WorkflowPlan, 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compose an integrated response that synthesizes results from multiple agents.
        """
        # Use LLM to create a coherent summary
        summary_prompt = f"""
        Create a comprehensive engineering project summary based on these agent results:
        
        Workflow: {workflow_plan.workflow_id}
        Completed Tasks: {len([t for t in workflow_plan.tasks if t.status == 'completed'])}
        
        Results Summary:
        {self._format_results_for_summary(results)}
        
        Create a professional project summary that integrates all findings:
        """
        
        try:
            integrated_summary = await self.llm_client.generate(summary_prompt)
        except:
            integrated_summary = "Automated workflow completed successfully with multiple disciplinary analyses."
        
        return {
            'workflow_summary': integrated_summary,
            'task_results': results,
            'workflow_plan': workflow_plan.__dict__,
            'execution_stats': {
                'total_tasks': len(workflow_plan.tasks),
                'completed_tasks': len([t for t in workflow_plan.tasks if t.status == 'completed']),
                'failed_tasks': len([t for t in workflow_plan.tasks if t.status == 'failed']),
                'estimated_duration': workflow_plan.estimated_duration,
                'agents_used': [t.agent_type for t in workflow_plan.tasks]
            }
        }
    
    def _format_results_for_summary(self, results: Dict[str, Any]) -> str:
        """Format results for LLM summary generation."""
        formatted = []
        for task_id, result in results.items():
            if result.get('status') == 'success':
                messages = result.get('messages', ['Task completed'])
                formatted.append(f"- {task_id}: {messages[0] if messages else 'Completed'}")
        return '\n'.join(formatted)
    
    async def _get_agent(self, agent_type: str):
        """Get agent instance by type."""
        # Import agents dynamically to avoid circular imports
        if agent_type == 'structural':
            from .structural_agent import StructuralDesignAgent
            return StructuralDesignAgent(self.session_id, self.meta)
        elif agent_type == 'civil':
            from .civil_agent import CivilDesignAgent
            return CivilDesignAgent(self.session_id, self.meta)
        elif agent_type == 'mechanical':
            from .mechanical_agent import MechanicalDesignAgent
            return MechanicalDesignAgent(self.session_id, self.meta)
        elif agent_type == 'electrical':
            from .electrical_agent import ElectricalDesignAgent
            return ElectricalDesignAgent(self.session_id, self.meta)
        elif agent_type == 'interior':
            from .interior_agent import InteriorDesignAgent
            return InteriorDesignAgent(self.session_id, self.meta)
        elif agent_type == 'bom':
            from .bom_agent import BOMAgent
            return BOMAgent(self.session_id, self.meta)
        elif agent_type == 'compliance':
            from .compliance_agent import ComplianceAgent
            return ComplianceAgent(self.session_id, self.meta)
        elif agent_type == 'qa':
            from .drawing_qa_agent import DrawingQAAgent
            return DrawingQAAgent(self.session_id, self.meta)
        elif agent_type == 'sustainability':
            from .sustainability_agent import SustainabilityAgent
            return SustainabilityAgent(self.session_id, self.meta)
        elif agent_type == 'generative':
            from .generative_design_agent import GenerativeDesignAgent
            return GenerativeDesignAgent(self.session_id, self.meta)
        elif agent_type == 'planning':
            from .planning_engineer_agent import PlanningEngineerAgent
            return PlanningEngineerAgent(self.session_id, self.meta)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")