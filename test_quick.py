#!/usr/bin/env python3
"""
Quick test script to validate the AI Design Suite is working.
Run this to verify basic functionality without pytest.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.llm.llm_client import MockLLMClient
from agents.root_agent import RootAgent
from agents.structural_agent import StructuralDesignAgent


async def test_basic_functionality():
    """Test basic functionality of the AI Design Suite."""
    
    print("Testing AI Design Suite Basic Functionality")
    print("=" * 50)
    
    # Setup mock services
    mock_meta = {
        'llm_client': MockLLMClient([
            'Mock structural engineering response',
            'Beam design analysis complete',
            'Safety factors applied successfully'
        ]),
        'asset_registry': {},
        'supplier_db': {},
        'cad_services': None,
        'config': {
            'temp_dir': './temp',
            'output_dir': './outputs',
            'session_dir': './sessions'
        }
    }
    
    try:
        # Test 1: Basic Root Agent
        print("\n1. Testing Root Agent...")
        root_agent = RootAgent(session_id='test-basic', meta=mock_meta)
        
        simple_request = {
            'message': 'Hello, what can you help me with?',
            'intent': 'general'
        }
        
        result = await root_agent.run(simple_request)
        print(f"   [OK] Root Agent Response: {result['status']}")
        print(f"   Messages: {len(result['messages'])} message(s)")
        
        # Test 2: Structural Agent
        print("\n2. Testing Structural Agent...")
        structural_request = {
            'message': 'Design a steel beam for 10m span with 50kN/m load',
            'intent': 'structural',
            'params': {
                'intent': 'beam_design',
                'span': 10.0,
                'load': 50.0,
                'material': 'steel',
                'safety_factor': 1.5
            }
        }
        
        result = await root_agent.run(structural_request)
        print(f"   [OK] Structural Agent Response: {result['status']}")
        
        if result['status'] == 'success' and 'selected_section' in result['data']:
            section = result['data']['selected_section']
            print(f"   Selected Section: {section['name']}")
            print(f"   Utilization: {section['utilization']:.2%}")
        
        # Test 3: Generative Design Agent
        print("\n3. Testing Generative Design Agent...")
        generative_request = {
            'message': 'Generate 3 parametric variations',
            'intent': 'generative',
            'params': {
                'intent': 'parametric_variations',
                'base_parameters': {
                    'span': 8.0,
                    'load': 35.0,
                    'material': 'steel'
                },
                'count': 3
            }
        }
        
        result = await root_agent.run(generative_request)
        print(f"   [OK] Generative Agent Response: {result['status']}")
        
        if result['status'] == 'success' and 'variations' in result['data']:
            variations = result['data']['variations']
            print(f"   Generated {len(variations)} variations")
            for i, var in enumerate(variations):
                print(f"      Variation {i+1}: Score {var['metrics']['score']:.3f}")
        
        # Test 4: Multi-Agent Workflow
        print("\n4. Testing Multi-Agent Workflow...")
        multi_request = {
            'message': 'Design structure and estimate costs',
            'multi_agent': True,
            'agents': ['structural', 'bom']
        }
        
        result = await root_agent.run(multi_request)
        print(f"   [OK] Multi-Agent Response: {result['status']}")
        print(f"   Workflow Type: {result['metadata']['workflow_type']}")
        print(f"   Agents Used: {', '.join(result['metadata']['agents_used'])}")
        
        # Test 5: Available Agents
        print("\n5. Testing Available Agents List...")
        available_agents = root_agent.get_available_agents()
        print(f"   [OK] Found {len(available_agents)} available agents:")
        for agent_type in sorted(available_agents.keys()):
            print(f"      * {agent_type}: {available_agents[agent_type][:50]}...")
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("\nNext steps:")
        print("   * Run 'python app.py' to start the web server")
        print("   * Run 'python app.py --cli' for interactive mode")
        print("   * Visit http://localhost:8000/docs for API documentation")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from agents.root_agent import RootAgent
        from agents.structural_agent import StructuralDesignAgent
        from agents.civil_agent import CivilDesignAgent
        from agents.mechanical_agent import MechanicalDesignAgent
        from agents.electrical_agent import ElectricalDesignAgent
        from agents.interior_agent import InteriorDesignAgent
        from agents.bom_agent import BOMAgent
        from agents.compliance_agent import ComplianceAgent
        from agents.drawing_qa_agent import DrawingQAAgent
        from agents.sustainability_agent import SustainabilityAgent
        from agents.generative_design_agent import GenerativeDesignAgent
        from services.llm.llm_client import MockLLMClient, create_llm_client
        
        print("   [OK] All agent imports successful")
        print("   [OK] All service imports successful")
        return True
        
    except ImportError as e:
        print(f"   [ERROR] Import failed: {e}")
        return False


if __name__ == "__main__":
    print("AI Design Suite - Quick Test")
    print("=" * 40)
    
    # Test imports first
    if not test_imports():
        print("[ERROR] Import test failed. Please check your Python environment.")
        sys.exit(1)
    
    # Test basic functionality
    success = asyncio.run(test_basic_functionality())
    
    if success:
        print("\nReady to run the AI Design Suite!")
        sys.exit(0)
    else:
        print("\n[ERROR] Tests failed. Please check the error messages above.")
        sys.exit(1)