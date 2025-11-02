"""
Agent module initialization.
Imports all agent classes for easy access.
"""

from .root_agent import RootAgent
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
from .automated_workflow_agent import AutomatedWorkflowAgent

__all__ = [
    "RootAgent",
    "DesignCopilotAgent",
    "CivilDesignAgent", 
    "StructuralDesignAgent",
    "MechanicalDesignAgent",
    "ElectricalDesignAgent",
    "InteriorDesignAgent",
    "BOMAgent",
    "ComplianceAgent",
    "DrawingQAAgent",
    "SustainabilityAgent",
    "GenerativeDesignAgent",
    "AutomatedWorkflowAgent"
]

def get_available_agents():
    """Return list of available agent names"""
    # Remove 'Agent' suffix and convert to lowercase
    agent_names = []
    for agent_class in __all__:
        if agent_class == "RootAgent":
            agent_names.append("root")
        else:
            # Convert CamelCase to snake_case and remove 'Agent' suffix
            name = agent_class.replace("Agent", "")
            # Convert CamelCase to snake_case
            import re
            name = re.sub('([A-Z]+)', r'_\1', name).lower().strip('_')
            agent_names.append(name)
    return sorted(agent_names)