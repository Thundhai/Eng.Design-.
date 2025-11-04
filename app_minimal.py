# File: app_minimal.py
"""
AI Design Suite - Minimal Version for Railway Deployment
Simplified version without Microsoft Agent Framework dependencies
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
import uvicorn
from datetime import datetime, timezone
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uuid
import json

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


# ============================================================================
# Pydantic Models for API
# ============================================================================

class SessionCreateRequest(BaseModel):
    """Request model for creating a new session."""
    description: str = Field(..., description="Description of the design task")
    user_id: Optional[str] = Field(None, description="User identifier")


class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="User message")
    agent_type: Optional[str] = Field(None, description="Specific agent to use")
    multi_agent: bool = Field(False, description="Use multi-agent workflow")
    files: Optional[List[str]] = Field(None, description="Uploaded file paths")


class SessionResponse(BaseModel):
    """Response model for session operations."""
    session_id: str
    status: str
    created_at: str
    description: str


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    status: str
    data: Dict[str, Any]
    messages: List[str]
    files: List[str]
    metadata: Dict[str, Any]
    next_actions: List[str]


# ============================================================================
# Simple Mock Agent System
# ============================================================================

class MockAgent:
    """Simple mock agent that provides engineering responses."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        
        # Agent-specific responses
        self.responses = {
            'structural': {
                'messages': [
                    f"✅ Structural Analysis Complete",
                    f"For your structural design requirements, I recommend:",
                    f"• Steel beam: W16x31 for 10m span",
                    f"• Load capacity: 50kN/m uniformly distributed",
                    f"• Safety factor: 2.5 (exceeds code requirements)",
                    f"• Deflection: L/250 = 40mm (within limits)"
                ],
                'data': {
                    'beam_size': 'W16x31',
                    'span': '10m',
                    'load_capacity': '50kN/m',
                    'safety_factor': 2.5,
                    'deflection': '40mm',
                    'material': 'Grade 50 Steel'
                }
            },
            'civil': {
                'messages': [
                    f"🏗️ Civil Engineering Analysis Complete",
                    f"Site planning recommendations:",
                    f"• Foundation: Spread footing design",
                    f"• Drainage: French drain system recommended",
                    f"• Site access: 6m wide access road",
                    f"• Utilities: Underground placement preferred"
                ],
                'data': {
                    'foundation_type': 'Spread footing',
                    'drainage_system': 'French drain',
                    'access_width': '6m',
                    'utilities': 'Underground'
                }
            },
            'electrical': {
                'messages': [
                    f"⚡ Electrical System Design Complete",
                    f"Power distribution recommendations:",
                    f"• Main panel: 200A service entrance",
                    f"• Branch circuits: 20A GFCI protected",
                    f"• Lighting: LED fixtures, 3000K color temp",
                    f"• Emergency power: Generator backup recommended"
                ],
                'data': {
                    'main_panel': '200A',
                    'branch_circuits': '20A GFCI',
                    'lighting': 'LED 3000K',
                    'backup_power': 'Generator'
                }
            },
            'mechanical': {
                'messages': [
                    f"🔧 Mechanical Design Analysis Complete",
                    f"Assembly design recommendations:",
                    f"• Tolerances: ±0.1mm for critical dimensions",
                    f"• Materials: Aluminum 6061-T6",
                    f"• Fasteners: Stainless steel bolts",
                    f"• Finishing: Anodized coating"
                ],
                'data': {
                    'tolerance': '±0.1mm',
                    'material': 'Aluminum 6061-T6',
                    'fasteners': 'Stainless steel',
                    'finish': 'Anodized'
                }
            },
            'bom': {
                'messages': [
                    f"💰 Bill of Materials Generated",
                    f"Cost analysis summary:",
                    f"• Materials: $15,000",
                    f"• Labor: $8,000",
                    f"• Equipment: $3,000",
                    f"• Total estimated cost: $26,000"
                ],
                'data': {
                    'materials_cost': 15000,
                    'labor_cost': 8000,
                    'equipment_cost': 3000,
                    'total_cost': 26000,
                    'currency': 'USD'
                }
            }
        }
    
    async def process(self, message: str) -> Dict[str, Any]:
        """Process a message and return agent response."""
        
        # Get agent-specific response or default
        response_data = self.responses.get(self.agent_type, {
            'messages': [
                f"🤖 {self.agent_type.title()} Agent Response",
                f"I've analyzed your request: '{message[:50]}...'",
                f"Based on engineering best practices, I recommend:",
                f"• Professional consultation for detailed analysis",
                f"• Code compliance verification",
                f"• Quality assurance review"
            ],
            'data': {
                'agent_type': self.agent_type,
                'message_received': message[:100],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        })
        
        return {
            'status': 'success',
            'data': response_data['data'],
            'messages': response_data['messages'],
            'files': [],
            'metadata': {
                'agent_type': self.agent_type,
                'session_id': 'mock-session',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'processing_time': '1.2s'
            },
            'next_actions': [
                'Request detailed calculations',
                'Upload technical drawings',
                'Schedule engineering review'
            ]
        }


class MockRootAgent:
    """Mock root agent that routes to specialized agents."""
    
    def __init__(self):
        self.available_agents = {
            'structural': 'Building structures, beams, columns, foundations, load analysis',
            'civil': 'Site planning, earthworks, drainage, road design',
            'electrical': 'Circuits, wiring, lighting, power distribution, schematics',
            'mechanical': 'Assemblies, mechanisms, tolerances, manufacturing design',
            'interior': 'Space planning, furniture layouts, finishes, materials',
            'bom': 'Bill of materials, costing, procurement, supplier management',
            'compliance': 'Code compliance, standards checking, regulations',
            'qa': 'Quality assurance, drawing review, clash detection',
            'sustainability': 'Environmental impact, carbon footprint, LCA analysis',
            'generative': 'Parametric design, optimization, design variations',
            'general': 'General design questions and multi-disciplinary coordination'
        }
    
    def detect_agent_type(self, message: str) -> str:
        """Detect which agent should handle the message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['beam', 'column', 'structure', 'load', 'foundation']):
            return 'structural'
        elif any(word in message_lower for word in ['site', 'drainage', 'civil', 'earthwork']):
            return 'civil'
        elif any(word in message_lower for word in ['electrical', 'power', 'lighting', 'circuit']):
            return 'electrical'
        elif any(word in message_lower for word in ['mechanical', 'assembly', 'tolerance']):
            return 'mechanical'
        elif any(word in message_lower for word in ['cost', 'bom', 'material', 'price']):
            return 'bom'
        else:
            return 'general'
    
    async def process(self, message: str, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Process message through appropriate agent."""
        
        # Determine agent type
        if not agent_type:
            agent_type = self.detect_agent_type(message)
        
        # Create and run agent
        agent = MockAgent(agent_type)
        return await agent.process(message)


# ============================================================================
# Application State
# ============================================================================

class AppState:
    """Application state management."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.root_agent = MockRootAgent()
        self.initialized = False
    
    async def initialize(self):
        """Initialize application services."""
        if self.initialized:
            return
        
        # Create necessary directories
        for directory in ['./temp', './outputs', './sessions']:
            os.makedirs(directory, exist_ok=True)
        
        self.initialized = True
        print(f"✅ AI Design Suite initialized with Mock Agents")


# ============================================================================
# FastAPI Application Setup
# ============================================================================

# Global application state
state = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global state
    
    # Startup
    print("🚀 Starting AI Design Suite Web Server...")
    state = AppState()
    await state.initialize()
    
    yield
    
    # Shutdown (if needed)
    pass

app = FastAPI(
    title="AI Design Suite",
    description="Comprehensive multi-disciplinary design engineering AI agent suite",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for web UI (Firebase-friendly)
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',') if os.getenv('CORS_ORIGINS') else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "llm_provider": "mock",
        "initialized": state.initialized,
        "available_agents": len(state.root_agent.available_agents)
    }


@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new design session."""
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "description": request.description,
        "user_id": request.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "messages": [],
        "files": []
    }
    
    state.sessions[session_id] = session_data
    
    return SessionResponse(
        session_id=session_id,
        status="created",
        created_at=session_data["created_at"],
        description=request.description
    )


@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    if session_id not in state.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return state.sessions[session_id]


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the design agents."""
    if request.session_id not in state.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Process through mock agents
        result = await state.root_agent.process(request.message, request.agent_type)
        
        # Store interaction in session
        session = state.sessions[request.session_id]
        session["messages"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": request.message,
            "agent_response": result,
            "agent_type": request.agent_type
        })
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/api/v1/upload")
async def upload_file(session_id: str = Form(...), file: UploadFile = File(...)):
    """Upload a CAD or reference file."""
    if session_id not in state.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Save uploaded file
        file_path = f"./temp/{session_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Mock file analysis
        file_info = {
            "filename": file.filename,
            "size": len(content),
            "type": file.content_type,
            "status": "uploaded"
        }
        
        # Update session
        session = state.sessions[session_id]
        session["files"].append({
            "filename": file.filename,
            "path": file_path,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "info": file_info
        })
        
        return {
            "status": "uploaded",
            "filename": file.filename,
            "path": file_path,
            "info": file_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/v1/agents")
async def get_available_agents():
    """Get list of available agents and their capabilities."""
    return {
        "agents": state.root_agent.available_agents,
        "total_agents": len(state.root_agent.available_agents),
        "status": "active"
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Design Suite")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"), help="Host for web server")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), help="Port for web server")
    
    args = parser.parse_args()
    
    print("🚀 Starting AI Design Suite Web Server...")
    print(f"📖 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🎯 Health Check: http://{args.host}:{args.port}/health")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )