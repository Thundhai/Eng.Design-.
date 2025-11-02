# AI Design Suite

A comprehensive multi-disciplinary AI agent suite for design engineers covering Civil, Mechanical, Electrical, Structural, and Interior design disciplines.

## Features

- **Multi-Agent Architecture**: Specialized agents for different engineering disciplines
- **Microsoft Agent Framework**: Built on the latest Microsoft Agent Framework for Python
- **Orchestrated Workflows**: RootAgent coordinates between specialized agents
- **CAD Integration**: Support for DWG, DXF, STEP, IFC file formats
- **Compliance Checking**: Automated code compliance and standards verification
- **BOM Generation**: Automated Bill of Materials and cost estimation
- **Sustainability Analysis**: LCA checks and carbon footprint estimation
- **Voice Interface**: Optional voice input/output capabilities
- **Offline-First**: Local LLM support with cloud fallback

## Agent Suite

1. **RootAgent**: Orchestrator that routes requests and manages sessions
2. **DesignCopilotAgent**: Conversational front-end interface
3. **CivilDesignAgent**: Earthworks, site layouts, drainage, roads
4. **StructuralDesignAgent**: Beam/column sizing, load calculations, FEA
5. **MechanicalDesignAgent**: Assemblies, tolerances, mechanisms
6. **ElectricalDesignAgent**: Schematics, load calculations, cable sizing
7. **InteriorDesignAgent**: Space planning, furniture layouts, materials
8. **BOMAgent**: Procurement and costing analysis
9. **ComplianceAgent**: Standards checking (NIS, ISO, ASME, IEC)
10. **DrawingQAAgent**: Review and error detection
11. **SustainabilityAgent**: LCA and environmental impact analysis
12. **GenerativeDesignAgent**: Parametric variations and optimization
13. **ReportAgent**: Formatted deliverable generation
14. **VoiceAgent**: Speech-to-text and text-to-speech
15. **ReflectiveAgent**: Decision explanation and audit trail

## Installation

### Quick Start (Recommended)

⚠️ **Important**: The `--pre` flag is required because Microsoft Agent Framework and Azure AI Inference are in preview.

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install core dependencies (WORKING!)
pip install --pre -r requirements.txt

# Install basic optional features (file processing, CAD support)
pip install -r requirements-basic-optional.txt
```

### Advanced Installation (Optional CAD Features)

For advanced CAD functionality, some packages require special installation:

```bash
# FreeCAD integration (system installation required)
# 1. Download from https://www.freecadweb.org/
# 2. Install system-wide
# 3. Test: python -c "import FreeCAD"

# Advanced CAD with conda (recommended for complex features)
conda create -n ai-design-cad python=3.11
conda activate ai-design-cad
conda install -c conda-forge pythonocc-core ifcopenshell
pip install --pre -r requirements.txt
```

### Docker Installation (All Dependencies Included)

```bash
# Build and run with all dependencies pre-installed
docker-compose up -d

# Access at http://localhost:8000
```

## Configuration

Create a `.env` file in the project root:

```env
# LLM Configuration
LLM_PROVIDER=azure_ai_foundry  # or 'local' or 'openai'
AZURE_AI_ENDPOINT=your_azure_ai_endpoint
AZURE_AI_MODEL_DEPLOYMENT=your_model_deployment

# Optional: Local LLM
LOCAL_LLM_ENDPOINT=http://localhost:11434  # Ollama default

# Azure Authentication (uses DefaultAzureCredential)
# Make sure you're logged in with: az login

# File paths
CAD_TEMP_DIR=./temp
OUTPUT_DIR=./outputs
SESSION_DIR=./sessions
```

## Quick Start

### 1. Run Tests
```bash
pytest tests/ -v
```

### 2. Start the API Server
```bash
python app.py
```

### 3. Test Basic Functionality
```bash
# Health check
curl http://localhost:8000/health

# Create a new session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"description": "Structural beam design"}'

# Send a design request
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "message": "Design a steel beam for a 10m span with 50kN/m load",
    "agent_type": "structural"
  }'
```

### 4. CLI Usage
```bash
# Interactive mode
python app.py --cli

# Direct command
python app.py --cli --message "Design a residential electrical layout for 200sqm house" --agent electrical
```

## Project Structure

```
ai-design-suite/
├── agents/                    # Specialized design agents
│   ├── base_agent.py         # Base agent interface
│   ├── root_agent.py         # Main orchestrator
│   ├── design_copilot_agent.py
│   ├── civil_agent.py
│   ├── structural_agent.py
│   ├── mechanical_agent.py
│   ├── electrical_agent.py
│   ├── interior_agent.py
│   ├── bom_agent.py
│   ├── compliance_agent.py
│   ├── drawing_qa_agent.py
│   ├── sustainability_agent.py
│   └── generative_design_agent.py
├── services/                  # Core services
│   ├── cad/                  # CAD file handling
│   │   ├── converters.py
│   │   └── freecad_interface.py
│   ├── analysis/             # Engineering analysis
│   │   └── simple_fea.py
│   ├── llm/                  # LLM abstraction
│   │   └── llm_client.py
│   └── supplier_db.py        # Supplier database
├── utils/                     # Utilities
│   ├── io.py                 # File I/O helpers
│   ├── session.py            # Session management
│   ├── prompts.py            # Prompt templates
│   └── validators.py         # Input validation
├── tests/                     # Test suite
├── sessions/                  # Session storage
├── outputs/                   # Generated outputs
├── temp/                      # Temporary files
├── requirements.txt
├── Dockerfile
├── .env.example
├── app.py                     # Main application
└── README.md
```

## Development Tasks

### Setup Development Environment
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt

# Run linting
black .
flake8 .
mypy .
```

### Run All Tests
```bash
pytest tests/ -v --cov=agents --cov=services
```

### Build Docker Image
```bash
docker build -t ai-design-suite .
docker run -p 8000:8000 ai-design-suite
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{session_id}` - Get session details
- `POST /api/v1/chat` - Send message to agents
- `POST /api/v1/upload` - Upload CAD files
- `GET /api/v1/reports/{session_id}` - Download reports

## Agent Examples

### Structural Design
```python
from agents.structural_agent import StructuralAgent

# Initialize with session
agent = StructuralAgent(session_id="123", meta={"llm_client": llm})

# Design request
result = await agent.run({
    "intent": "beam_design",
    "params": {
        "span": 10.0,  # meters
        "load": 50.0,  # kN/m
        "material": "steel",
        "safety_factor": 1.5
    }
})
```

### Multi-Agent Workflow
```python
from agents.root_agent import RootAgent

# Orchestrated design workflow
root = RootAgent(session_id="456")
result = await root.run({
    "message": "Design a 3-story office building structure and MEP systems",
    "files": ["site_plan.dwg", "architectural_drawings.pdf"]
})
```

## CAD Integration

Supported formats:
- **Input**: DWG, DXF, STEP, IFC, PDF, Images
- **Output**: DWG, DXF, STEP, IFC, PDF reports

Example usage:
```python
from services.cad.converters import dwg_to_dxf, ifc_load

# Convert CAD file
dxf_path = await dwg_to_dxf("input.dwg")

# Load IFC model
ifc_model = await ifc_load("building.ifc")
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Roadmap

- [ ] Enhanced CAD integrations (Autodesk, SolidWorks APIs)
- [ ] Advanced FEA solver integration
- [ ] Real-time collaboration features
- [ ] Mobile app interface
- [ ] Cloud deployment templates
- [ ] Industry-specific agent templates

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review example code in `tests/`

---

Built with ❤️ using Microsoft Agent Framework