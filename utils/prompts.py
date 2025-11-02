# File: utils/prompts.py
"""
Prompt templates and utilities for the AI Design Suite.

Contains carefully crafted prompts for different engineering disciplines
and design tasks to ensure consistent, high-quality outputs.
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for different agents and tasks."""
    
    # Structural Engineering Prompts
    STRUCTURAL_BEAM_SIZING = """
    You are a structural engineering expert. Design a beam with the following requirements:
    
    **Design Parameters:**
    - Span: {span} meters
    - Load: {load} kN/m (uniformly distributed)
    - Material: {material}
    - Safety Factor: {safety_factor}
    - Design Code: {design_code}
    
    **Required Analysis:**
    1. Calculate design moment and shear
    2. Select appropriate beam section
    3. Check bending stress
    4. Check deflection (limit: span/250)
    5. Check shear stress
    6. Provide recommendations
    
    Be specific about section sizes, material grades, and code references.
    Include safety considerations and constructability comments.
    """
    
    STRUCTURAL_COLUMN_DESIGN = """
    You are a structural engineering expert. Design a column with these requirements:
    
    **Design Parameters:**
    - Height: {height} meters
    - Axial Load: {axial_load} kN
    - Moment: {moment} kNm (if applicable)
    - Material: {material}
    - End Conditions: {end_conditions}
    - Design Code: {design_code}
    
    **Analysis Required:**
    1. Calculate slenderness ratio
    2. Check buckling capacity
    3. Check combined loading (if applicable)
    4. Select section size
    5. Verify connections
    
    Provide detailed calculations and code references.
    """
    
    # Civil Engineering Prompts
    CIVIL_SITE_LAYOUT = """
    You are a civil engineering expert specializing in site planning. 
    
    **Project Requirements:**
    - Site Area: {site_area} m²
    - Building Type: {building_type}
    - Local Climate: {climate}
    - Soil Conditions: {soil_conditions}
    - Access Requirements: {access_requirements}
    
    **Design Considerations:**
    1. Optimal building orientation
    2. Drainage and stormwater management
    3. Access roads and parking
    4. Utility routing
    5. Landscaping and environmental impact
    6. Local zoning compliance
    
    Provide a comprehensive site layout strategy with rationale.
    """
    
    # Electrical Engineering Prompts
    ELECTRICAL_LOAD_CALCULATION = """
    You are an electrical engineering expert. Calculate electrical loads for:
    
    **Building Information:**
    - Building Type: {building_type}
    - Total Area: {area} m²
    - Occupancy: {occupancy} people
    - Operating Hours: {operating_hours}
    
    **Load Categories to Calculate:**
    1. Lighting loads (W/m²)
    2. Power outlets and equipment
    3. HVAC electrical requirements
    4. Special equipment loads
    5. Safety and emergency systems
    
    **Deliverables:**
    - Load schedule by circuit
    - Panel sizing recommendations
    - Cable sizing calculations
    - Diversity factors applied
    
    Follow relevant electrical codes (IEC/NEC) and provide safety margins.
    """
    
    # Mechanical Engineering Prompts
    MECHANICAL_ASSEMBLY_DESIGN = """
    You are a mechanical engineering expert. Design an assembly with:
    
    **Requirements:**
    - Function: {function}
    - Operating Conditions: {operating_conditions}
    - Materials: {materials}
    - Manufacturing Method: {manufacturing_method}
    - Tolerance Requirements: {tolerances}
    
    **Design Considerations:**
    1. Component geometry and interfaces
    2. Material selection rationale
    3. Manufacturing feasibility
    4. Assembly sequence
    5. Tolerance stack-up analysis
    6. Maintenance accessibility
    
    Provide detailed drawings, material specifications, and assembly instructions.
    """
    
    # Interior Design Prompts
    INTERIOR_SPACE_PLANNING = """
    You are an interior design expert. Plan a space with these requirements:
    
    **Space Information:**
    - Space Type: {space_type}
    - Area: {area} m²
    - Occupancy: {occupancy}
    - Budget Level: {budget_level}
    - Style Preference: {style}
    
    **Design Elements:**
    1. Space allocation and flow
    2. Furniture selection and layout
    3. Color scheme and materials
    4. Lighting design
    5. Storage solutions
    6. Accessibility considerations
    
    Create a cohesive design that balances functionality, aesthetics, and budget.
    """
    
    # Compliance and Quality Prompts
    COMPLIANCE_CODE_CHECK = """
    You are a code compliance expert. Review this design against:
    
    **Applicable Codes:**
    - Building Code: {building_code}
    - Design Standard: {design_standard}
    - Local Regulations: {local_regulations}
    
    **Design Details:**
    {design_details}
    
    **Check Items:**
    1. Structural requirements
    2. Fire safety provisions
    3. Accessibility compliance
    4. Environmental requirements
    5. Safety factors and margins
    
    **Deliverable:**
    Compliance report with:
    - Conforming items ✅
    - Non-conforming items ❌
    - Recommendations for corrections
    - Required documentation
    """
    
    # Sustainability Prompts
    SUSTAINABILITY_ANALYSIS = """
    You are a sustainability expert. Analyze the environmental impact of:
    
    **Project Details:**
    - Project Type: {project_type}
    - Materials: {materials}
    - Energy Systems: {energy_systems}
    - Location: {location}
    
    **Analysis Areas:**
    1. Carbon footprint calculation
    2. Material lifecycle assessment
    3. Energy efficiency evaluation
    4. Water usage and management
    5. Waste generation and recycling
    6. Alternative material suggestions
    
    **Targets:**
    - Carbon reduction opportunities
    - LEED/BREEAM considerations
    - Cost-benefit analysis of green alternatives
    
    Provide actionable recommendations for improved sustainability.
    """
    
    # BOM and Costing Prompts
    BOM_COST_ANALYSIS = """
    You are a procurement and costing expert. Analyze:
    
    **Project Scope:**
    {project_scope}
    
    **Material List:**
    {material_list}
    
    **Analysis Required:**
    1. Complete Bill of Materials
    2. Current market pricing
    3. Supplier recommendations
    4. Lead time analysis
    5. Alternative material options
    6. Cost optimization opportunities
    
    **Deliverables:**
    - Detailed BOM with quantities
    - Cost breakdown by category
    - Risk assessment (price volatility)
    - Procurement schedule
    - Value engineering suggestions
    """


def load_prompt(prompt_name: str, **kwargs) -> str:
    """
    Load and format a prompt template.
    
    Args:
        prompt_name: Name of the prompt template
        **kwargs: Variables to substitute in the template
        
    Returns:
        Formatted prompt string
    """
    templates = PromptTemplates()
    
    # Convert prompt name to attribute name
    attr_name = prompt_name.upper()
    
    if hasattr(templates, attr_name):
        template = getattr(templates, attr_name)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for prompt '{prompt_name}': {e}")
    else:
        raise ValueError(f"Prompt template '{prompt_name}' not found")


def get_available_prompts() -> Dict[str, str]:
    """Get list of available prompt templates."""
    templates = PromptTemplates()
    
    prompts = {}
    for attr_name in dir(templates):
        if not attr_name.startswith('_') and attr_name.isupper():
            # Convert back to readable name
            readable_name = attr_name.lower()
            prompts[readable_name] = f"Prompt template for {readable_name.replace('_', ' ')}"
    
    return prompts


def create_custom_prompt(base_template: str, custom_instructions: str, **variables) -> str:
    """
    Create a custom prompt by combining base template with additional instructions.
    
    Args:
        base_template: Name of base prompt template
        custom_instructions: Additional instructions to append
        **variables: Template variables
        
    Returns:
        Custom formatted prompt
    """
    base_prompt = load_prompt(base_template, **variables)
    
    custom_prompt = f"""
    {base_prompt}
    
    **Additional Instructions:**
    {custom_instructions}
    """
    
    return custom_prompt.strip()


# Specialized prompt builders for complex scenarios
class PromptBuilder:
    """Builder for creating complex, multi-part prompts."""
    
    def __init__(self):
        self.sections = []
    
    def add_context(self, context: str) -> 'PromptBuilder':
        """Add context section to prompt."""
        self.sections.append(f"**Context:**\n{context}")
        return self
    
    def add_requirements(self, requirements: list) -> 'PromptBuilder':
        """Add requirements list to prompt."""
        req_text = "\n".join([f"- {req}" for req in requirements])
        self.sections.append(f"**Requirements:**\n{req_text}")
        return self
    
    def add_constraints(self, constraints: list) -> 'PromptBuilder':
        """Add constraints list to prompt."""
        const_text = "\n".join([f"- {const}" for const in constraints])
        self.sections.append(f"**Constraints:**\n{const_text}")
        return self
    
    def add_deliverables(self, deliverables: list) -> 'PromptBuilder':
        """Add expected deliverables to prompt."""
        deliv_text = "\n".join([f"- {deliv}" for deliv in deliverables])
        self.sections.append(f"**Expected Deliverables:**\n{deliv_text}")
        return self
    
    def add_examples(self, examples: list) -> 'PromptBuilder':
        """Add examples to prompt."""
        example_text = "\n".join([f"Example: {ex}" for ex in examples])
        self.sections.append(f"**Examples:**\n{example_text}")
        return self
    
    def build(self, role: str = "engineering expert") -> str:
        """Build the final prompt."""
        header = f"You are a {role}."
        
        if not self.sections:
            return header
        
        return header + "\n\n" + "\n\n".join(self.sections)


# Common prompt fragments for reuse
class PromptFragments:
    """Reusable prompt fragments."""
    
    SAFETY_DISCLAIMER = """
    **Important:** This analysis is for preliminary design purposes only. 
    All designs must be reviewed and approved by licensed professionals 
    before implementation. Local codes and standards take precedence.
    """
    
    CODE_COMPLIANCE = """
    **Code Compliance:** Ensure all recommendations comply with applicable 
    local building codes, design standards, and regulatory requirements.
    """
    
    PROFESSIONAL_REVIEW = """
    **Professional Review Required:** This design requires review and 
    approval by a licensed professional engineer before construction.
    """
    
    COST_DISCLAIMER = """
    **Cost Estimates:** Pricing is indicative and based on current market 
    conditions. Obtain formal quotes from suppliers for accurate costing.
    """