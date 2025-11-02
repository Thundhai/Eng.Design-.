# File: tests/test_integration.py
"""
Integration tests for the AI Design Suite.

Tests the complete workflow from API endpoints to agent execution
to validate the system works end-to-end.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm.llm_client import MockLLMClient
from agents.root_agent import RootAgent
from agents.structural_agent import StructuralDesignAgent


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def mock_meta(self):
        """Create mock meta dictionary for testing."""
        return {
            'llm_client': MockLLMClient([
                'This is a mock response for structural engineering queries.',
                'Mock beam design recommendation: Use IPE300 section.',
                'Mock analysis complete with safety factors applied.'
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
    
    @pytest.mark.asyncio
    async def test_structural_beam_design_workflow(self, mock_meta):
        """Test complete structural beam design workflow."""
        # Create root agent
        root_agent = RootAgent(session_id='test-integration', meta=mock_meta)
        
        # Test beam design request
        beam_request = {
            'message': 'Design a steel beam for 10m span with 50kN/m load',
            'intent': 'structural',
            'params': {
                'span': 10.0,
                'load': 50.0,
                'material': 'steel',
                'safety_factor': 1.5
            }
        }
        
        # Execute the request
        result = await root_agent.run(beam_request)
        
        # Validate response structure
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'data' in result
        assert 'messages' in result
        assert 'metadata' in result
        
        # Check that routing worked
        assert 'routing' in result['metadata']
        assert 'structural' in result['metadata']['routing']['intent_classified']
        
        print(f"✅ Beam design test passed: {result['status']}")
    
    @pytest.mark.asyncio
    async def test_multi_agent_workflow(self, mock_meta):
        """Test multi-agent workflow coordination."""
        root_agent = RootAgent(session_id='test-multi-agent', meta=mock_meta)
        
        # Request involving multiple agents
        multi_request = {
            'message': 'Design a building structure and generate cost estimate',
            'multi_agent': True,
            'agents': ['structural', 'bom']
        }
        
        result = await root_agent.run(multi_request)
        
        # Validate multi-agent response
        assert result['metadata']['workflow_type'] == 'multi_agent'
        assert len(result['metadata']['agents_used']) >= 2
        
        print(f"✅ Multi-agent test passed: {result['status']}")
    
    @pytest.mark.asyncio
    async def test_generative_design_variations(self, mock_meta):
        """Test generative design agent parametric variations."""
        root_agent = RootAgent(session_id='test-generative', meta=mock_meta)
        
        # Request parametric variations
        generative_request = {
            'message': 'Generate 3 parametric variations for beam design',
            'intent': 'generative',
            'params': {
                'intent': 'parametric_variations',
                'base_parameters': {
                    'span': 12.0,
                    'load': 40.0,
                    'material': 'steel'
                },
                'count': 3,
                'range': 0.15
            }
        }
        
        result = await root_agent.run(generative_request)
        
        # Validate generative design response
        assert 'variations' in result['data']
        assert len(result['data']['variations']) == 3
        
        # Check that each variation has required structure
        for variation in result['data']['variations']:
            assert 'variation_id' in variation
            assert 'parameters' in variation
            assert 'metrics' in variation
        
        print(f"✅ Generative design test passed: {result['status']}")
    
    @pytest.mark.asyncio
    async def test_agent_caching(self, mock_meta):
        """Test that agents are properly cached for reuse."""
        root_agent = RootAgent(session_id='test-caching', meta=mock_meta)
        
        # First request
        await root_agent.run({'message': 'Test structural query', 'intent': 'structural'})
        
        # Check agent was cached
        assert 'structural' in root_agent._agent_cache
        cached_agent = root_agent._agent_cache['structural']
        
        # Second request should reuse cached agent
        await root_agent.run({'message': 'Another structural query', 'intent': 'structural'})
        
        # Should be the same instance
        assert root_agent._agent_cache['structural'] is cached_agent
        
        print("✅ Agent caching test passed")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_meta):
        """Test error handling for invalid requests."""
        root_agent = RootAgent(session_id='test-errors', meta=mock_meta)
        
        # Test with invalid parameters
        invalid_request = {
            'message': 'Test with invalid data',
            'params': {
                'invalid_param': 'invalid_value'
            }
        }
        
        result = await root_agent.run(invalid_request)
        
        # Should handle gracefully without crashing
        assert 'status' in result
        assert isinstance(result['messages'], list)
        
        print(f"✅ Error handling test passed: {result['status']}")
    
    def test_available_agents_list(self, mock_meta):
        """Test getting list of available agents."""
        root_agent = RootAgent(session_id='test-agents-list', meta=mock_meta)
        
        available_agents = root_agent.get_available_agents()
        
        # Check that all expected agents are available
        expected_agents = [
            'structural', 'civil', 'mechanical', 'electrical', 'interior',
            'bom', 'compliance', 'qa', 'sustainability', 'generative', 'general'
        ]
        
        for agent_type in expected_agents:
            assert agent_type in available_agents
            assert isinstance(available_agents[agent_type], str)
            assert len(available_agents[agent_type]) > 0
        
        print(f"✅ Available agents test passed: {len(available_agents)} agents found")


@pytest.mark.asyncio
async def test_structural_agent_direct():
    """Test structural agent directly without root agent."""
    mock_meta = {
        'llm_client': MockLLMClient(['Mock structural analysis complete']),
        'asset_registry': {},
        'supplier_db': {},
        'cad_services': None,
        'config': {}
    }
    
    structural_agent = StructuralDesignAgent(session_id='test-direct', meta=mock_meta)
    
    # Test beam design
    beam_input = {
        'intent': 'beam_design',
        'params': {
            'span': 8.0,
            'load': 35.0,
            'material': 'steel',
            'safety_factor': 1.5
        }
    }
    
    result = await structural_agent.run(beam_input)
    
    assert result['status'] == 'success'
    assert 'selected_section' in result['data']
    assert 'checks' in result['data']
    
    print("✅ Direct structural agent test passed")


if __name__ == '__main__':
    # Run tests manually for development
    async def run_tests():
        test_instance = TestIntegration()
        
        mock_meta = {
            'llm_client': MockLLMClient([
                'Mock response for testing',
                'Structural analysis complete',
                'Design recommendations provided'
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
        
        print("🧪 Running AI Design Suite Integration Tests...")
        
        try:
            await test_instance.test_structural_beam_design_workflow(mock_meta)
            await test_instance.test_multi_agent_workflow(mock_meta)
            await test_instance.test_generative_design_variations(mock_meta)
            await test_instance.test_agent_caching(mock_meta)
            await test_instance.test_error_handling(mock_meta)
            test_instance.test_available_agents_list(mock_meta)
            await test_structural_agent_direct()
            
            print("\n🎉 All integration tests passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise
    
    # Run the tests
    asyncio.run(run_tests())