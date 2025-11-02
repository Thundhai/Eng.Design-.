# File: agents/structural_agent.py
"""
Structural Design Agent - Specialized agent for structural engineering tasks.

Handles beam design, column sizing, load calculations, foundation design,
and structural analysis using engineering principles and code compliance.
"""

from typing import Any, Dict, Optional
import math
from .base_agent import BaseAgent


class StructuralDesignAgent(BaseAgent):
    """
    Specialized agent for structural engineering design and analysis.
    
    Capabilities:
    - Beam and column design
    - Load calculations and combinations
    - Foundation design
    - Simple structural analysis
    - Code compliance checking
    - Material selection
    """
    
    def __init__(self, session_id: str, meta: Dict[str, Any]):
        super().__init__(session_id, meta)
        self.agent_description = "Structural engineering design and analysis"
        
        # Material properties database (simplified)
        self.materials = {
            'steel': {
                'fy': 250,  # MPa, yield strength
                'fu': 400,  # MPa, ultimate strength
                'E': 200000,  # MPa, elastic modulus
                'density': 7850  # kg/m³
            },
            'concrete': {
                'fc': 25,  # MPa, compressive strength
                'ft': 2.5,  # MPa, tensile strength
                'E': 25000,  # MPa, elastic modulus
                'density': 2400  # kg/m³
            },
            'timber': {
                'fb': 40,  # MPa, bending strength
                'ft': 30,  # MPa, tensile strength
                'E': 12000,  # MPa, elastic modulus
                'density': 600  # kg/m³
            }
        }
        
        # Standard sections database (simplified)
        self.steel_sections = {
            'IPE200': {'h': 200, 'b': 100, 'tw': 5.6, 'tf': 8.5, 'A': 28.5, 'Ix': 1943, 'Wx': 194},
            'IPE300': {'h': 300, 'b': 150, 'tw': 7.1, 'tf': 10.7, 'A': 53.8, 'Ix': 8356, 'Wx': 557},
            'IPE400': {'h': 400, 'b': 180, 'tw': 8.6, 'tf': 13.5, 'A': 84.5, 'Ix': 23130, 'Wx': 1156},
            'IPE500': {'h': 500, 'b': 200, 'tw': 10.2, 'tf': 16.0, 'A': 116.0, 'Ix': 48200, 'Wx': 1928}
        }
    
    async def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process structural design requests.
        
        Supported intents:
        - beam_design: Design beams for given loads and spans
        - column_design: Design columns for axial and combined loads
        - foundation_design: Design foundations
        - load_analysis: Calculate load combinations
        - section_properties: Calculate section properties
        - deflection_check: Check deflection limits
        """
        try:
            intent = input.get('intent', 'general')
            params = input.get('params', {})
            
            self.log_activity(f"Processing structural request: {intent}")
            
            # Route to specific handler
            if intent == 'beam_design':
                return await self._design_beam(params)
            elif intent == 'column_design':
                return await self._design_column(params)
            elif intent == 'foundation_design':
                return await self._design_foundation(params)
            elif intent == 'load_analysis':
                return await self._analyze_loads(params)
            elif intent == 'section_properties':
                return await self._calculate_section_properties(params)
            elif intent == 'deflection_check':
                return await self._check_deflection(params)
            else:
                return await self._handle_general_structural_query(input)
                
        except Exception as e:
            self.log_activity(f"Error in structural agent: {str(e)}", 'error')
            return self.create_error_response(f"Structural design failed: {str(e)}")
    
    async def _design_beam(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Design a beam for given span and loading."""
        try:
            # Extract parameters
            span = float(params.get('span', 0))  # meters
            load = float(params.get('load', 0))  # kN/m (UDL)
            material = params.get('material', 'steel').lower()
            safety_factor = float(params.get('safety_factor', 1.5))
            
            # Validate inputs
            if span <= 0 or load <= 0:
                return self.create_error_response("Invalid span or load values")
            
            # Calculate design moment
            design_moment = (load * span**2) / 8 * safety_factor  # kNm
            
            # Select appropriate section
            selected_section = self._select_beam_section(design_moment, material, span)
            
            if not selected_section:
                return self.create_error_response("No suitable section found")
            
            # Perform detailed checks
            checks = await self._perform_beam_checks(selected_section, design_moment, span, load)
            
            result_data = {
                'design_parameters': {
                    'span': span,
                    'load': load,
                    'material': material,
                    'safety_factor': safety_factor,
                    'design_moment': round(design_moment, 2)
                },
                'selected_section': selected_section,
                'checks': checks,
                'recommendations': self._generate_beam_recommendations(checks)
            }
            
            message = f"""
            ✅ **Beam Design Complete**
            
            **Design Parameters:**
            • Span: {span}m
            • Load: {load} kN/m
            • Material: {material.title()}
            • Design Moment: {design_moment:.2f} kNm
            
            **Selected Section:** {selected_section['name']}
            • Depth: {selected_section['properties']['h']}mm
            • Width: {selected_section['properties']['b']}mm
            • Section Modulus: {selected_section['properties']['Wx']} cm³
            
            **Design Checks:**
            • Bending: {'✅ PASS' if checks['bending']['pass'] else '❌ FAIL'}
            • Deflection: {'✅ PASS' if checks['deflection']['pass'] else '❌ FAIL'}
            • Shear: {'✅ PASS' if checks['shear']['pass'] else '❌ FAIL'}
            """
            
            return self.create_success_response(result_data, message)
            
        except Exception as e:
            return self.create_error_response(f"Beam design calculation failed: {str(e)}")
    
    def _select_beam_section(self, design_moment: float, material: str, span: float) -> Optional[Dict[str, Any]]:
        """Select appropriate beam section based on moment requirement."""
        if material == 'steel':
            material_props = self.materials['steel']
            allowable_stress = material_props['fy'] / 1.5  # MPa with factor of safety
            
            # Required section modulus in mm³
            required_wx = (design_moment * 1e6) / allowable_stress
            
            # Find suitable section
            for section_name, props in self.steel_sections.items():
                section_wx = props['Wx'] * 1000  # Convert to mm³
                if section_wx >= required_wx:
                    return {
                        'name': section_name,
                        'properties': props,
                        'material': material,
                        'utilization': required_wx / section_wx
                    }
        
        return None
    
    async def _perform_beam_checks(self, section: Dict[str, Any], moment: float, span: float, load: float) -> Dict[str, Any]:
        """Perform comprehensive beam design checks."""
        props = section['properties']
        material = self.materials[section['material']]
        
        # Bending check
        actual_stress = (moment * 1e6) / (props['Wx'] * 1000)  # MPa
        allowable_stress = material['fy'] / 1.5
        bending_utilization = actual_stress / allowable_stress
        
        # Deflection check (simplified)
        # δ = 5wL⁴/(384EI) for UDL
        deflection = (5 * load * 1000 * (span * 1000)**4) / (384 * material['E'] * props['Ix'] * 1e4)  # mm
        allowable_deflection = (span * 1000) / 250  # L/250
        deflection_utilization = deflection / allowable_deflection
        
        # Shear check (simplified)
        max_shear = (load * span) / 2  # kN
        # Simplified shear stress calculation
        shear_stress = (max_shear * 1000) / (props['A'] * 100)  # MPa (rough approximation)
        allowable_shear = material['fy'] / (1.5 * 1.732)  # Von Mises criterion
        shear_utilization = shear_stress / allowable_shear
        
        return {
            'bending': {
                'actual_stress': round(actual_stress, 2),
                'allowable_stress': round(allowable_stress, 2),
                'utilization': round(bending_utilization, 3),
                'pass': bending_utilization <= 1.0
            },
            'deflection': {
                'actual_deflection': round(deflection, 2),
                'allowable_deflection': round(allowable_deflection, 2),
                'utilization': round(deflection_utilization, 3),
                'pass': deflection_utilization <= 1.0
            },
            'shear': {
                'actual_stress': round(shear_stress, 2),
                'allowable_stress': round(allowable_shear, 2),
                'utilization': round(shear_utilization, 3),
                'pass': shear_utilization <= 1.0
            }
        }
    
    def _generate_beam_recommendations(self, checks: Dict[str, Any]) -> list[str]:
        """Generate design recommendations based on check results."""
        recommendations = []
        
        if not checks['bending']['pass']:
            recommendations.append("⚠️ Increase section size or use higher strength material for bending")
        
        if not checks['deflection']['pass']:
            recommendations.append("⚠️ Increase section depth or add intermediate supports for deflection")
        
        if not checks['shear']['pass']:
            recommendations.append("⚠️ Check web design or add shear reinforcement")
        
        if checks['bending']['utilization'] > 0.9:
            recommendations.append("💡 Consider slightly larger section for better safety margin")
        
        if all(check['pass'] for check in checks.values()):
            recommendations.append("✅ Design meets all requirements")
            
            if max(check['utilization'] for check in checks.values()) < 0.6:
                recommendations.append("💡 Consider optimizing to smaller section for economy")
        
        return recommendations
    
    async def _design_column(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Design a column for axial and bending loads."""
        # Placeholder for column design
        return self.create_success_response(
            {'status': 'Column design placeholder'},
            "Column design feature coming soon"
        )
    
    async def _design_foundation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Design foundation elements."""
        # Placeholder for foundation design
        return self.create_success_response(
            {'status': 'Foundation design placeholder'},
            "Foundation design feature coming soon"
        )
    
    async def _analyze_loads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and combine loads according to codes."""
        # Placeholder for load analysis
        return self.create_success_response(
            {'status': 'Load analysis placeholder'},
            "Load combination analysis feature coming soon"
        )
    
    async def _calculate_section_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate section properties for custom sections."""
        # Placeholder for section properties calculation
        return self.create_success_response(
            {'status': 'Section properties placeholder'},
            "Custom section properties calculation coming soon"
        )
    
    async def _check_deflection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check deflection for existing members."""
        # Placeholder for deflection check
        return self.create_success_response(
            {'status': 'Deflection check placeholder'},
            "Deflection checking feature coming soon"
        )
    
    async def _handle_general_structural_query(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general structural engineering questions using LLM."""
        message = input.get('message', '')
        
        if not self.llm_client:
            return self.create_warning_response(
                {'query': message},
                "LLM not available for general queries. Please use specific structural intents."
            )
        
        # Enhanced prompt for structural engineering context
        enhanced_prompt = f"""
        You are a structural engineering expert assistant. Provide accurate, code-compliant 
        guidance on structural design topics including:
        
        - Beam and column design
        - Load calculations and combinations
        - Foundation design principles
        - Material selection
        - Code requirements (focus on Eurocode/IS codes)
        - Construction best practices
        
        Always emphasize safety, code compliance, and the need for professional review.
        
        User query: {message}
        
        Provide practical engineering guidance:
        """
        
        try:
            response = await self.llm_client.generate(enhanced_prompt)
            
            return self.create_success_response(
                {'response': response, 'query': message},
                response
            )
            
        except Exception as e:
            return self.create_error_response(f"Failed to generate structural guidance: {str(e)}")