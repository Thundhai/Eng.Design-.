# File: app.py
"""
AI Design Suite - Main Application Entry Point

Provides both FastAPI web server and CLI interface for the design engineering
agent suite. Supports REST API endpoints and command-line operations.
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

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Import our agents and services
from agents.root_agent import RootAgent
from services.llm.llm_client import create_llm_client, MockLLMClient
from services.cad.converters import CADConverters
from utils.prompts import get_available_prompts


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
    
    # Create necessary directories
    for directory in ['./temp', './outputs', './sessions']:
        os.makedirs(directory, exist_ok=True)
    
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

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Application State and Configuration
# ============================================================================

class AppState:
    """Application state management."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.llm_client = None
        self.cad_converter = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize application services."""
        if self.initialized:
            return
        
        try:
            # Initialize LLM client based on environment
            provider = os.getenv('LLM_PROVIDER', 'mock')
            
            if provider.lower() == 'mock':
                # Use mock client for testing
                self.llm_client = MockLLMClient([
                    "I'm here to help with your design engineering needs!",
                    "Let me analyze your structural requirements...",
                    "Based on the parameters provided, here are my recommendations..."
                ])
            else:
                # Use real LLM client
                self.llm_client = create_llm_client(provider)
            
            # Initialize CAD converter
            self.cad_converter = CADConverters()
            
            self.initialized = True
            print(f"✅ AI Design Suite initialized with LLM provider: {provider}")
            
        except Exception as e:
            print(f"⚠️ Warning: LLM initialization failed: {e}")
            print("🔄 Falling back to mock client for development")
            self.llm_client = MockLLMClient()
            self.cad_converter = CADConverters()
            self.initialized = True
    
    def get_meta(self) -> Dict[str, Any]:
        """Get meta dictionary for agents."""
        return {
            'llm_client': self.llm_client,
            'asset_registry': {},  # TODO: Implement asset registry
            'supplier_db': {},     # TODO: Implement supplier database
            'cad_services': self.cad_converter,
            'config': {
                'temp_dir': './temp',
                'output_dir': './outputs',
                'session_dir': './sessions'
            }
        }


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
        "llm_provider": os.getenv('LLM_PROVIDER', 'mock'),
        "initialized": state.initialized
    }


@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create a new design session."""
    import uuid
    
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
        # Create root agent for this session
        root_agent = RootAgent(session_id=request.session_id, meta=state.get_meta())
        
        # Prepare input for agent
        agent_input = {
            'message': request.message,
            'intent': request.agent_type,
            'multi_agent': request.multi_agent,
            'files': request.files or []
        }
        
        # Execute agent
        result = await root_agent.run(agent_input)
        
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
        
        # Analyze file if it's a CAD file
        if state.cad_converter:
            file_info = await state.cad_converter.extract_drawing_info(file_path)
        else:
            file_info = {"filename": file.filename, "size": len(content)}
        
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
    # Create a temporary root agent to get agent info
    temp_root = RootAgent(session_id="temp", meta=state.get_meta())
    
    return {
        "agents": temp_root.get_available_agents(),
        "prompts": get_available_prompts()
    }


@app.get("/api/v1/reports/{session_id}")
async def download_report(session_id: str):
    """Download generated reports for a session."""
    if session_id not in state.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # TODO: Implement report generation
    report_path = f"./outputs/{session_id}_report.pdf"
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(report_path, filename=f"design_report_{session_id}.pdf")


# ============================================================================
# CLI Interface
# ============================================================================

async def cli_main(parsed_args=None):
    """Command-line interface main function."""
    global state
    
    if parsed_args is None:
        parser = argparse.ArgumentParser(description="AI Design Suite CLI")
        parser.add_argument("--message", "-m", help="Design message/query")
        parser.add_argument("--agent", "-a", help="Specific agent to use")
        parser.add_argument("--file", "-f", help="Input file path")
        parser.add_argument("--output", "-o", help="Output directory")
        parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
        parser.add_argument("--cli", action="store_true", help="Start interactive CLI mode")
        
        parsed_args = parser.parse_args()
    
    # Initialize application state for CLI mode
    if state is None:
        print("🚀 Starting AI Design Suite CLI...")
        state = AppState()
        await state.initialize()
        
        # Create necessary directories
        for directory in ['./temp', './outputs', './sessions']:
            os.makedirs(directory, exist_ok=True)
        
        print("✅ AI Design Suite initialized with LLM provider:", os.getenv('LLM_PROVIDER', 'mock'))
    
    if parsed_args.interactive or parsed_args.cli:
        await interactive_cli()
    else:
        await single_command_cli(parsed_args)


async def interactive_cli():
    """Interactive CLI mode."""
    print("🤖 AI Design Suite - Interactive Mode")
    print("Type 'help' for available commands, 'quit' to exit")
    
    # Create a session for the CLI
    session_id = "cli-session"
    root_agent = RootAgent(session_id=session_id, meta=state.get_meta())
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print_cli_help()
                continue
            
            if not user_input:
                continue
            
            # Process the input
            print("🔄 Processing...")
            result = await root_agent.run({'message': user_input})
            
            # Display result
            print(f"\n📝 Status: {result['status']}")
            for message in result['messages']:
                print(f"💬 {message}")
            
            if result.get('next_actions'):
                print("\n🎯 Suggested next actions:")
                for action in result['next_actions']:
                    print(f"   • {action}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def single_command_cli(args):
    """Single command CLI mode."""
    if not args.message:
        print("❌ Error: Message required for single command mode")
        return
    
    # Create session and agent
    session_id = "cli-single"
    root_agent = RootAgent(session_id=session_id, meta=state.get_meta())
    
    # Prepare input
    agent_input = {'message': args.message}
    if args.agent:
        agent_input['intent'] = args.agent
    if args.file:
        agent_input['files'] = [args.file]
    
    # Execute
    print(f"🔄 Processing: {args.message}")
    result = await root_agent.run(agent_input)
    
    # Display result
    print(f"\n📝 Status: {result['status']}")
    for message in result['messages']:
        print(f"💬 {message}")
    
    # Save output if specified
    if args.output:
        import json
        output_file = Path(args.output) / f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"💾 Results saved to: {output_file}")


def print_cli_help():
    """Print CLI help information."""
    help_text = """
🤖 AI Design Suite - Available Commands:

Design Commands:
• Design a beam for 10m span with 50kN/m load
• Create electrical layout for office building
• Generate BOM for steel structure
• Check code compliance for foundation design
• Optimize design for minimum weight

Agent-Specific Commands:
• structural: Building design, beam/column sizing
• civil: Site planning, earthworks, roads
• electrical: Circuits, wiring, power systems
• mechanical: Assemblies, mechanisms, tolerances
• interior: Space planning, furniture layouts
• bom: Material lists, cost estimation
• compliance: Code checking, standards
• qa: Quality control, drawing review
• sustainability: Environmental analysis
• generative: Design optimization

General Commands:
• help - Show this help
• quit/exit/q - Exit the application

Example:
> Design a steel beam for 12m span with 75kN/m UDL using structural agent
"""
    print(help_text)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Parse arguments for both CLI and web server modes
    parser = argparse.ArgumentParser(description="AI Design Suite")
    parser.add_argument("--cli", action="store_true", help="Start interactive CLI mode")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive CLI mode")
    parser.add_argument("--message", "-m", help="Design message/query")
    parser.add_argument("--agent", "-a", help="Specific agent to use")
    parser.add_argument("--file", "-f", help="Input file path")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--host", default="0.0.0.0", help="Host for web server")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server")
    
    args = parser.parse_args()
    
    # Check if CLI mode is requested
    if args.cli or args.interactive or args.message:
        # CLI mode - pass the parsed args to avoid double parsing
        asyncio.run(cli_main(args))
    else:
        # Web server mode
        print("🚀 Starting AI Design Suite Web Server...")
        print(f"📖 API Documentation: http://{args.host}:{args.port}/docs")
        print(f"🎯 Health Check: http://{args.host}:{args.port}/health")
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info"
        )