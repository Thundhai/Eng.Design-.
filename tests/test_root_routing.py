# File: tests/test_root_routing.py
"""
Tests for the Root Agent routing functionality.

Tests the intent classification, agent routing, and multi-agent workflow
capabilities of the RootAgent orchestrator.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from agents.root_agent import RootAgent
from agents.design_copilot_agent import DesignCopilotAgent
from agents.structural_agent import StructuralDesignAgent
from services.llm.llm_client import MockLLMClient


class TestRootAgentRouting:
    """Test cases for RootAgent routing functionality."""
    
    @pytest.fixture
    def mock_meta(self):
        """Create mock meta dictionary with required services."""
        return {
            'llm_client': MockLLMClient(['Mock response from LLM']),
            'asset_registry': {},
            'supplier_db': {},
            'cad_services': {},
            'config': {}
        }
    
    @pytest.fixture
    def root_agent(self, mock_meta):
        """Create RootAgent instance for testing."""
        return RootAgent(session_id='test-session-123', meta=mock_meta)
    
    @pytest.mark.asyncio
    async def test_explicit_intent_routing(self, root_agent):
        """Test routing with explicit intent specified."""
        input_data = {
            'message': 'Design a beam',
            'intent': 'structural',
            'params': {'span': 10, 'load': 50}
        }
        
        result = await root_agent.run(input_data)
        
        assert result['status'] in ['success', 'warning', 'error']
        assert 'metadata' in result
        assert 'routing' in result['metadata']
        assert result['metadata']['routing']['intent_classified'] == ['structural']
    
    @pytest.mark.asyncio
    async def test_keyword_based_intent_classification(self, root_agent):
        """Test intent classification based on keywords in message."""
        test_cases = [
            ('Design a steel beam for 10m span', ['structural']),
            ('Create electrical wiring layout', ['electrical']),
            ('Plan interior space layout', ['interior']),
            ('Generate bill of materials', ['bom']),
            ('Check building code compliance', ['compliance'])
        ]
        
        for message, expected_intents in test_cases:
            input_data = {'message': message}
            
            # Mock the classification to return expected intents
            classified_intents = await root_agent._classify_intent(input_data)
            
            # Should contain at least one expected intent
            assert any(intent in classified_intents for intent in expected_intents), \
                f"Expected one of {expected_intents} in {classified_intents} for message: {message}"
    
    @pytest.mark.asyncio
    async def test_multi_agent_workflow_flag(self, root_agent):
        """Test multi-agent workflow when explicitly requested."""
        input_data = {
            'message': 'Design a complete building structure',
            'multi_agent': True,
            'agents': ['structural', 'bom', 'compliance']
        }
        
        result = await root_agent.run(input_data)
        
        assert result['status'] in ['success', 'warning', 'error']
        assert result['metadata']['workflow_type'] == 'multi_agent'
        assert len(result['metadata']['agents_used']) >= 2
    
    @pytest.mark.asyncio
    async def test_default_to_general_agent(self, root_agent):
        """Test that unclear intents default to general/copilot agent."""
        input_data = {
            'message': 'Hello, what can you help me with?'
        }
        
        classified_intents = await root_agent._classify_intent(input_data)
        
        # Should default to general if no specific intent detected
        assert 'general' in classified_intents or len(classified_intents) == 0
    
    @pytest.mark.asyncio
    async def test_agent_caching(self, root_agent):
        """Test that agents are cached for reuse within session."""
        # First request
        input_data1 = {'message': 'Design a beam', 'intent': 'structural'}
        await root_agent.run(input_data1)
        
        # Second request with same intent
        input_data2 = {'message': 'Calculate beam deflection', 'intent': 'structural'}
        await root_agent.run(input_data2)
        
        # Should have cached the structural agent
        assert 'structural' in root_agent._agent_cache
        assert isinstance(root_agent._agent_cache['structural'], StructuralDesignAgent)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, root_agent):
        """Test error handling for invalid inputs."""
        # Test with invalid agent type
        input_data = {
            'message': 'Test message',
            'intent': 'nonexistent_agent'
        }
        
        result = await root_agent.run(input_data)
        
        # Should gracefully handle unknown agent types
        assert result['status'] in ['success', 'warning', 'error']
    
    @pytest.mark.asyncio
    async def test_session_context_injection(self, root_agent):
        """Test that session context is properly injected into input."""
        input_data = {'message': 'Test message'}
        
        enhanced_input = root_agent._enhance_input(input_data)
        
        assert 'session_context' in enhanced_input
        assert enhanced_input['session_context']['session_id'] == 'test-session-123'
        assert 'timestamp' in enhanced_input
    
    def test_available_agents_list(self, root_agent):
        """Test getting list of available agents."""
        available_agents = root_agent.get_available_agents()
        
        assert isinstance(available_agents, dict)
        assert 'structural' in available_agents
        assert 'civil' in available_agents
        assert 'electrical' in available_agents
        assert 'mechanical' in available_agents
        assert 'interior' in available_agents
        
        # Check descriptions are provided
        for agent_type, description in available_agents.items():
            assert isinstance(description, str)
            assert len(description) > 0


class TestIntentClassification:
    """Test cases specifically for intent classification logic."""
    
    @pytest.fixture
    def mock_meta(self):
        """Create mock meta dictionary."""
        return {
            'llm_client': MockLLMClient(['structural']),  # Mock LLM returns 'structural'
            'asset_registry': {},
            'supplier_db': {},
            'cad_services': {},
            'config': {}
        }
    
    @pytest.fixture
    def root_agent(self, mock_meta):
        """Create RootAgent instance for testing."""
        return RootAgent(session_id='test-session', meta=mock_meta)
    
    @pytest.mark.asyncio
    async def test_llm_classification_fallback(self, root_agent):
        """Test LLM classification when keywords don't match."""
        input_data = {
            'message': 'I need help with something complex that requires engineering analysis'
        }
        
        # Should use LLM for classification when no keywords match
        classified = await root_agent._classify_intent(input_data)
        
        # Mock LLM should return 'structural' based on fixture setup
        assert len(classified) > 0
    
    @pytest.mark.asyncio 
    async def test_explicit_intent_override(self, root_agent):
        """Test that explicit intent overrides keyword detection."""
        input_data = {
            'message': 'Design electrical wiring',  # Has electrical keywords
            'intent': 'structural'  # But explicitly requests structural
        }
        
        classified = await root_agent._classify_intent(input_data)
        
        assert classified == ['structural']
    
    @pytest.mark.asyncio
    async def test_multiple_keyword_detection(self, root_agent):
        """Test detection of multiple intents from keywords."""
        input_data = {
            'message': 'Design building structure with electrical systems and cost analysis'
        }
        
        classified = await root_agent._classify_intent(input_data)
        
        # Should detect multiple relevant intents
        expected_intents = ['structural', 'electrical', 'bom']
        found_intents = [intent for intent in expected_intents if any(intent in classified for intent in expected_intents)]
        
        assert len(found_intents) > 0


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])