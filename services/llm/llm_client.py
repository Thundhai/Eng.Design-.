# File: services/llm/llm_client.py
"""
LLM Client - Abstraction layer for Language Model interactions.

Supports multiple providers with a unified interface:
- Azure AI Foundry (recommended for production)
- OpenAI
- Local models (Ollama, etc.)
"""

import os
import asyncio
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized LLM response structure."""
    text: str
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate structured response with metadata."""
        pass


class AzureAIFoundryClient(BaseLLMClient):
    """Azure AI Foundry client using Microsoft Agent Framework."""
    
    def __init__(self, endpoint: str, model_deployment: str, credential=None):
        """
        Initialize Azure AI Foundry client.
        
        Args:
            endpoint: Azure AI Foundry project endpoint
            model_deployment: Model deployment name
            credential: Azure credential (uses DefaultAzureCredential if None)
        """
        self.endpoint = endpoint
        self.model_deployment = model_deployment
        self.credential = credential
        self._client = None
    
    async def _get_client(self):
        """Lazy initialization of the Azure client."""
        if self._client is None:
            try:
                from agent_framework_azure_ai import AzureAIAgentClient
                from azure.identity.aio import DefaultAzureCredential
                
                if self.credential is None:
                    self.credential = DefaultAzureCredential()
                
                self._client = AzureAIAgentClient(
                    project_endpoint=self.endpoint,
                    model_deployment_name=self.model_deployment,
                    async_credential=self.credential
                )
            except ImportError as e:
                raise ImportError(
                    "Azure AI dependencies not installed. "
                    "Run: pip install agent-framework-azure-ai --pre"
                ) from e
        
        return self._client
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Azure AI Foundry."""
        response = await self.generate_structured(prompt, **kwargs)
        return response.text
    
    async def generate_structured(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate structured response using Azure AI Foundry."""
        try:
            client = await self._get_client()
            
            # Create a simple agent for text generation
            from agent_framework import ChatAgent, ChatMessage, Role
            
            async with ChatAgent(chat_client=client) as agent:
                messages = [ChatMessage(Role.USER, text=prompt)]
                response = await agent.run(messages)
                
                return LLMResponse(
                    text=response.text,
                    model=self.model_deployment,
                    finish_reason="completed",
                    metadata={"provider": "azure_ai_foundry"}
                )
                
        except Exception as e:
            raise RuntimeError(f"Azure AI Foundry generation failed: {str(e)}") from e


class OpenAIClient(BaseLLMClient):
    """OpenAI client for API access."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self._client = None
    
    async def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError as e:
                raise ImportError(
                    "OpenAI dependencies not installed. "
                    "Run: pip install openai"
                ) from e
        
        return self._client
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI."""
        response = await self.generate_structured(prompt, **kwargs)
        return response.text
    
    async def generate_structured(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate structured response using OpenAI."""
        try:
            client = await self._get_client()
            
            # Prepare parameters
            params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            response = await client.chat.completions.create(**params)
            
            return LLMResponse(
                text=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                metadata={"provider": "openai"}
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {str(e)}") from e


class LocalLLMClient(BaseLLMClient):
    """Local LLM client (e.g., Ollama)."""
    
    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "llama3.2"):
        """
        Initialize local LLM client.
        
        Args:
            endpoint: Local LLM server endpoint
            model: Model name to use
        """
        self.endpoint = endpoint
        self.model = model
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using local LLM."""
        response = await self.generate_structured(prompt, **kwargs)
        return response.text
    
    async def generate_structured(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate structured response using local LLM."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                data = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_ctx": kwargs.get("max_tokens", 1000)
                    }
                }
                
                async with session.post(f"{self.endpoint}/api/generate", json=data) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Local LLM request failed: {response.status}")
                    
                    result = await response.json()
                    
                    return LLMResponse(
                        text=result.get("response", ""),
                        model=self.model,
                        finish_reason="completed",
                        metadata={
                            "provider": "local",
                            "endpoint": self.endpoint
                        }
                    )
                    
        except Exception as e:
            raise RuntimeError(f"Local LLM generation failed: {str(e)}") from e


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration."""
    
    @staticmethod
    def create_client(provider: str = None, **config) -> BaseLLMClient:
        """
        Create an LLM client based on provider and configuration.
        
        Args:
            provider: Provider name ('azure_ai_foundry', 'openai', 'local')
            **config: Provider-specific configuration
            
        Returns:
            Configured LLM client
        """
        # Auto-detect provider from environment if not specified
        if provider is None:
            provider = os.getenv('LLM_PROVIDER', 'mock')
        
        provider = provider.lower()
        
        if provider in ['azure_ai_foundry', 'azure']:
            endpoint = config.get('endpoint') or os.getenv('AZURE_AI_ENDPOINT')
            model = config.get('model') or os.getenv('AZURE_AI_MODEL_DEPLOYMENT')
            
            if not endpoint or not model:
                raise ValueError(
                    "Azure AI Foundry requires 'endpoint' and 'model' configuration. "
                    "Set AZURE_AI_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT environment variables."
                )
            
            return AzureAIFoundryClient(
                endpoint=endpoint,
                model_deployment=model,
                credential=config.get('credential')
            )
        
        elif provider == 'openai':
            api_key = config.get('api_key') or os.getenv('OPENAI_API_KEY')
            model = config.get('model', 'gpt-4o-mini')
            
            if not api_key:
                raise ValueError(
                    "OpenAI requires 'api_key' configuration. "
                    "Set OPENAI_API_KEY environment variable."
                )
            
            return OpenAIClient(api_key=api_key, model=model)
        
        elif provider == 'local':
            endpoint = config.get('endpoint', 'http://localhost:11434')
            model = config.get('model', 'llama3.2')
            
            return LocalLLMClient(endpoint=endpoint, model=model)
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self, mock_responses: Optional[List[str]] = None):
        """
        Initialize mock client.
        
        Args:
            mock_responses: List of responses to cycle through
        """
        self.mock_responses = mock_responses or ["Mock LLM response"]
        self.call_count = 0
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock text response."""
        response = await self.generate_structured(prompt, **kwargs)
        return response.text
    
    async def generate_structured(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate mock structured response."""
        # Simulate some delay
        await asyncio.sleep(0.1)
        
        # Generate contextual response based on prompt content
        try:
            response_text = self._generate_contextual_response(prompt)
        except Exception as e:
            print(f"[DEBUG] Error in contextual response: {e}")
            response_text = "Default response due to error"
            
        self.call_count += 1
        
        return LLMResponse(
            text=response_text,
            model="mock-model",
            finish_reason="completed",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            metadata={"provider": "mock", "call_count": self.call_count}
        )
    
    def _generate_contextual_response(self, prompt: str) -> str:
        """Generate contextual response based on prompt keywords."""
        prompt_lower = prompt.lower()
        
        # Generative design responses (check first to avoid conflicts)
        if any(word in prompt_lower for word in ['generate', 'parametric', 'variations', 'optimize', 'generative']):
            return """**Generative Design Results:**

Generated 3 optimized design variations:

**Variation 1:** Weight-optimized design (-15% mass)
**Variation 2:** Cost-optimized design (-12% cost)  
**Variation 3:** Performance-optimized design (+8% strength)

Each variation maintains safety factors and code compliance.
Parametric models available for further customization."""
        
        # Structural engineering responses
        elif any(word in prompt_lower for word in ['beam', 'steel', 'span', 'load', 'structural']):
            if 'beam' in prompt_lower and 'span' in prompt_lower:
                return """Based on the structural requirements:

**Steel Beam Design Analysis:**
- Span: 12m
- Load: 75 kN/m UDL
- Material: Steel Grade S355

**Recommended Section:** IPE 400
- Moment capacity: 362 kNm
- Shear capacity: 486 kN
- Deflection: L/350 (within limits)
- Utilization: 78% (safe design)

**Design Notes:**
- Supports required at both ends
- Fire protection recommended
- Check local buckling for concentrated loads
- Deflection limit: 34.3mm (actual: 28.1mm)

Design complies with Eurocode 3 standards."""
        
        # Civil engineering responses
        elif any(word in prompt_lower for word in ['site', 'drainage', 'earthwork', 'civil']):
            return """**Civil Engineering Analysis:**

Site assessment complete:
- Soil bearing capacity: 200 kN/m²
- Drainage requirements identified
- Access routes planned
- Utilities mapping complete

Recommendations provided for foundation design and site preparation."""
        
        # Mechanical engineering responses
        elif any(word in prompt_lower for word in ['mechanical', 'assembly', 'tolerance', 'manufacturing']):
            return """**Mechanical Design Analysis:**

Assembly requirements:
- Tolerance stack-up analysis complete
- Material selection: Grade 316 stainless steel
- Manufacturing process: CNC machining
- Quality control points identified

Design optimized for manufacturability and cost-effectiveness."""
        
        # Check for BOM keywords  
        elif 'procurement' in prompt_lower or 'bom' in prompt_lower or 'cost analysis' in prompt_lower:
            return """**Bill of Materials & Cost Analysis:**

Material List:
- Steel sections: €2,450
- Fasteners & connections: €485  
- Surface treatment: €320
- Installation labor: €1,200

**Total Estimated Cost: €4,455**

Lead times: 3-4 weeks for steel delivery
Suppliers identified and qualified."""
        
        # Workflow and automation responses
        elif any(word in prompt_lower for word in ['workflow', 'automated', 'comprehensive', 'complete project']):
            return """**Automated Workflow Analysis:**

Project scope analyzed successfully:
- Multi-disciplinary coordination required
- 5 primary agents identified for execution
- Sequential dependencies mapped
- Estimated completion: 12-15 hours

**Workflow Plan:**
1. Civil/Site Analysis → Structural Design
2. Structural → MEP Systems (parallel)
3. All systems → BOM & Cost Analysis
4. Final → Compliance & QA Review

Ready to execute automated workflow."""
        
        # Structural engineering responses
        if any(word in prompt_lower for word in ['beam', 'steel', 'span', 'load', 'structural']):
            if 'beam' in prompt_lower and 'span' in prompt_lower:
                return """Based on the structural requirements:

**Steel Beam Design Analysis:**
- Span: 12m
- Load: 75 kN/m UDL
- Material: Steel Grade S355

**Recommended Section:** IPE 400
- Moment capacity: 362 kNm
- Shear capacity: 486 kN
- Deflection: L/350 (within limits)
- Utilization: 78% (safe design)

**Design Notes:**
- Supports required at both ends
- Fire protection recommended
- Check local buckling for concentrated loads
- Deflection limit: 34.3mm (actual: 28.1mm)

Design complies with Eurocode 3 standards."""
        
        # Civil engineering responses
        elif any(word in prompt_lower for word in ['site', 'drainage', 'earthwork', 'civil']):
            return """**Civil Engineering Analysis:**

Site assessment complete:
- Soil bearing capacity: 200 kN/m²
- Drainage requirements identified
- Access routes planned
- Utilities mapping complete

Recommendations provided for foundation design and site preparation."""
        
        # Mechanical engineering responses
        elif any(word in prompt_lower for word in ['mechanical', 'assembly', 'tolerance', 'manufacturing']):
            return """**Mechanical Design Analysis:**

Assembly requirements:
- Tolerance stack-up analysis complete
- Material selection: Grade 316 stainless steel
- Manufacturing process: CNC machining
- Quality control points identified

Design optimized for manufacturability and cost-effectiveness."""
        
        # BOM/Cost responses
        elif any(word in prompt_lower for word in ['bom', 'cost', 'material', 'procurement', 'bill of materials']):
            print(f"[DEBUG] Matched BOM/Cost keywords")
            return """**Bill of Materials & Cost Analysis:**

Material List:
- Steel sections: €2,450
- Fasteners & connections: €485
- Surface treatment: €320
- Installation labor: €1,200

**Total Estimated Cost: €4,455**

Lead times: 3-4 weeks for steel delivery
Suppliers identified and qualified."""
        
        # Generative design responses
        elif any(word in prompt_lower for word in ['generate', 'parametric', 'variations', 'optimize']):
            return """**Generative Design Results:**

Generated 3 optimized design variations:

**Variation 1:** Weight-optimized design (-15% mass)
**Variation 2:** Cost-optimized design (-12% cost)  
**Variation 3:** Performance-optimized design (+8% strength)

Each variation maintains safety factors and code compliance.
Parametric models available for further customization."""
        
        # Default responses
        else:
            print(f"[DEBUG] No keywords matched, using default response")
            default_responses = [
                "I'm here to help with your design engineering needs!",
                "Analysis complete. Design recommendations provided.",
                "Engineering calculations verified. Results within acceptable parameters.",
                "Multi-disciplinary review completed successfully."
            ]
            return default_responses[self.call_count % len(default_responses)]


# Convenience function for quick setup
def create_llm_client(provider: str = None, **config) -> BaseLLMClient:
    """Create an LLM client with automatic configuration."""
    return LLMClientFactory.create_client(provider, **config)