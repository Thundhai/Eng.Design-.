# File: agents/design_copilot_agent.py
"""
Design Copilot Agent - Conversational front-end for the AI Design Suite.

Provides a friendly, intelligent interface that can handle general design questions,
coordinate with other agents, and provide guidance on using the system.
"""

from typing import Any, Dict, List
from .base_agent import BaseAgent


class DesignCopilotAgent(BaseAgent):
    """
    Conversational front-end agent for general design assistance.
    
    Handles:
    - General design questions
    - System guidance and help
    - Multi-disciplinary coordination
    - User onboarding and tutorials
    """
    
    def __init__(self, session_id: str, meta: Dict[str, Any]):
        super().__init__(session_id, meta)
        self.agent_description = "General design assistant and system coordinator"
    
    async def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process general design queries and provide assistance.
        
        Handles intents like:
        - general questions
        - help requests
        - system guidance
        - design methodology advice
        """
        try:
            message = input.get('message', '')
            intent = input.get('intent', 'general')
            
            self.log_activity(f"Processing copilot request: {intent}")
            
            # Route to specific handler based on intent
            if intent in ['help', 'guidance', 'tutorial']:
                return await self._handle_help_request(input)
            elif intent in ['agents', 'capabilities', 'features']:
                return await self._handle_capabilities_query(input)
            elif intent in ['methodology', 'process', 'workflow']:
                return await self._handle_methodology_query(input)
            else:
                return await self._handle_general_query(input)
                
        except Exception as e:
            self.log_activity(f"Error in copilot agent: {str(e)}", 'error')
            return self.create_error_response(f"Failed to process request: {str(e)}")
    
    async def _handle_help_request(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle help and guidance requests."""
        help_content = {
            'available_agents': {
                'civil': 'Site planning, earthworks, drainage, road design',
                'structural': 'Building structures, beams, columns, foundations',
                'mechanical': 'Assemblies, mechanisms, tolerances, manufacturing',
                'electrical': 'Circuits, wiring, lighting, power systems',
                'interior': 'Space planning, furniture, finishes, layouts',
                'bom': 'Bill of materials, costing, procurement',
                'compliance': 'Code checking, standards, regulations',
                'qa': 'Quality control, drawing review, clash detection',
                'sustainability': 'Environmental impact, carbon footprint',
                'generative': 'Parametric design, optimization, variations'
            },
            'example_queries': [
                "Design a steel beam for 10m span with 50kN/m load",
                "Create electrical layout for 200sqm office",
                "Check building code compliance for this design",
                "Generate BOM and cost estimate for this assembly",
                "Optimize this design for minimum weight",
                "Review these drawings for conflicts"
            ],
            'file_support': [
                "DWG/DXF: AutoCAD drawings",
                "STEP/IGES: 3D CAD models", 
                "IFC: Building information models",
                "PDF: Technical drawings and specs",
                "Images: Sketches and reference photos"
            ]
        }
        
        message = """
        🤖 **AI Design Suite Help**
        
        I'm your Design Copilot! I can help you with engineering design tasks across multiple disciplines.
        
        **Available Specialized Agents:**
        """ + "\n".join([f"• **{name.title()}**: {desc}" for name, desc in help_content['available_agents'].items()])
        
        message += """
        
        **Example Queries:**
        """ + "\n".join([f"• {query}" for query in help_content['example_queries']])
        
        message += """
        
        **Supported File Types:**
        """ + "\n".join([f"• {file_type}" for file_type in help_content['file_support']])
        
        message += """
        
        **Tips:**
        • Be specific about requirements (loads, dimensions, materials)
        • Upload relevant files for better context
        • Ask for multi-agent workflows for complex projects
        • Request compliance checking for regulatory requirements
        """
        
        return self.create_success_response(
            data=help_content,
            message=message
        )
    
    async def _handle_capabilities_query(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle queries about system capabilities."""
        capabilities = {
            'design_disciplines': [
                'Civil Engineering', 'Structural Engineering', 'Mechanical Engineering',
                'Electrical Engineering', 'Interior Design'
            ],
            'analysis_types': [
                'Structural FEA', 'Load Calculations', 'Code Compliance',
                'Clash Detection', 'Sustainability Analysis', 'Cost Estimation'
            ],
            'file_formats': {
                'input': ['DWG', 'DXF', 'STEP', 'IGES', 'IFC', 'PDF', 'Images'],
                'output': ['DWG', 'DXF', 'STEP', 'IFC', 'PDF Reports', 'Excel BOMs']
            },
            'integration_features': [
                'CAD Model Generation', 'Automated Drawing Creation',
                'BOM Generation', 'Cost Estimation', 'Compliance Reporting',
                'Multi-disciplinary Coordination'
            ]
        }
        
        if self.llm_client:
            # Generate detailed capability description using LLM
            prompt = f"""
            Based on these capabilities: {capabilities}
            
            Create a comprehensive but concise description of the AI Design Suite's 
            capabilities for engineering design. Focus on practical benefits and 
            real-world applications. Keep it professional but engaging.
            """
            
            response = await self.llm_client.generate(prompt)
            message = response
        else:
            message = "AI Design Suite provides comprehensive engineering design assistance across multiple disciplines."
        
        return self.create_success_response(
            data=capabilities,
            message=message
        )
    
    async def _handle_methodology_query(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle queries about design methodology and best practices."""
        methodology = {
            'design_process': [
                '1. Requirements Analysis',
                '2. Conceptual Design',
                '3. Detailed Design',
                '4. Analysis & Validation',
                '5. Compliance Check',
                '6. Documentation'
            ],
            'best_practices': [
                'Start with clear requirements and constraints',
                'Use appropriate safety factors and design codes',
                'Consider sustainability and lifecycle impacts',
                'Validate designs with analysis and testing',
                'Document decisions and assumptions',
                'Coordinate between disciplines early and often'
            ],
            'quality_gates': [
                'Requirements review',
                'Design review',
                'Analysis validation',
                'Code compliance check',
                'Peer review',
                'Final documentation review'
            ]
        }
        
        message = """
        📋 **Engineering Design Methodology**
        
        **Recommended Design Process:**
        """ + "\n".join(methodology['design_process'])
        
        message += """
        
        **Best Practices:**
        """ + "\n".join([f"• {practice}" for practice in methodology['best_practices']])
        
        message += """
        
        **Quality Gates:**
        """ + "\n".join([f"• {gate}" for gate in methodology['quality_gates']])
        
        return self.create_success_response(
            data=methodology,
            message=message
        )
    
    async def _handle_general_query(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general design questions using LLM."""
        message = input.get('message', '')
        
        if not self.llm_client:
            return self.create_warning_response(
                data={'message': message},
                warning="LLM not available. Please specify a more specific agent type."
            )
        
        # Enhance prompt with context about the design suite
        enhanced_prompt = f"""
        You are a helpful design engineering assistant part of the AI Design Suite.
        The suite includes specialized agents for civil, structural, mechanical, electrical,
        and interior design, plus tools for BOM generation, compliance checking, and sustainability analysis.
        
        User query: {message}
        
        Provide helpful, accurate engineering guidance. If the query is specific to a discipline,
        suggest using the appropriate specialized agent. Be professional but friendly.
        """
        
        try:
            response = await self.llm_client.generate(enhanced_prompt)
            
            # Add suggestions for follow-up actions
            next_actions = self._suggest_next_actions(message)
            
            result = self.create_success_response(
                data={'response': response, 'original_query': message},
                message=response
            )
            result['next_actions'] = next_actions
            
            return result
            
        except Exception as e:
            return self.create_error_response(f"Failed to generate response: {str(e)}")
    
    def _suggest_next_actions(self, message: str) -> List[str]:
        """Suggest relevant next actions based on the user's message."""
        suggestions = []
        message_lower = message.lower()
        
        # Suggest specific agents based on keywords
        if any(word in message_lower for word in ['beam', 'column', 'structure', 'load', 'foundation']):
            suggestions.append("Use the Structural Agent for detailed beam/column design")
        
        if any(word in message_lower for word in ['electrical', 'wiring', 'circuit', 'power', 'lighting']):
            suggestions.append("Use the Electrical Agent for circuit design and calculations")
        
        if any(word in message_lower for word in ['cost', 'material', 'bom', 'procurement']):
            suggestions.append("Use the BOM Agent for material lists and cost estimation")
        
        if any(word in message_lower for word in ['code', 'standard', 'regulation', 'compliance']):
            suggestions.append("Use the Compliance Agent for code checking")
        
        if any(word in message_lower for word in ['green', 'sustainable', 'carbon', 'environment']):
            suggestions.append("Use the Sustainability Agent for environmental analysis")
        
        # General suggestions if no specific matches
        if not suggestions:
            suggestions.extend([
                "Upload relevant CAD files for better context",
                "Specify material properties and design constraints",
                "Consider multi-agent workflow for complex projects"
            ])
        
        return suggestions[:3]  # Limit to top 3 suggestions