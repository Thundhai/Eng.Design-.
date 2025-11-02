# AI Design Suite - Quick Start Guide

## 🚀 Quick Start

The AI Design Suite is now ready to use! Here are the different ways to run it:

### 1. Web Server Mode (Recommended)
```bash
python app.py
```
Then visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Interactive CLI Mode
```bash
python app.py --cli
```

### 3. Single Command CLI
```bash
python app.py --message "Design a steel beam for 10m span with 50kN/m load" --agent structural
```

## ✅ Validation

Run the quick test to validate everything is working:
```bash
python test_quick.py
```

## 🔧 Configuration

1. Copy `.env.example` to `.env` and configure your settings:
```bash
cp .env.example .env
```

2. Edit `.env` to set your preferred LLM provider:
- `LLM_PROVIDER=mock` (for testing)
- `LLM_PROVIDER=azure_ai_foundry` (for production)
- `LLM_PROVIDER=openai` (alternative)
- `LLM_PROVIDER=local` (for Ollama/local models)

## 🤖 Available Agents

The suite includes 15 specialized agents:

1. **RootAgent** - Main orchestrator and router
2. **DesignCopilotAgent** - General design assistance
3. **CivilDesignAgent** - Site planning and infrastructure
4. **StructuralDesignAgent** - Building structures and analysis
5. **MechanicalDesignAgent** - Assemblies and mechanisms
6. **ElectricalDesignAgent** - Circuits and power systems
7. **InteriorDesignAgent** - Space planning and interiors
8. **BOMAgent** - Material lists and costing
9. **ComplianceAgent** - Code compliance checking
10. **DrawingQAAgent** - Quality assurance and review
11. **SustainabilityAgent** - Environmental impact analysis
12. **GenerativeDesignAgent** - Parametric design and optimization
13. **ReportAgent** - Documentation generation
14. **VoiceAgent** - Speech interface (optional)
15. **ReflectiveAgent** - Decision explanation and audit

## 📚 API Examples

### Create a Session
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"description": "Structural beam design project"}'
```

### Send Design Request
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "message": "Design a steel beam for a 10m span with 50kN/m load",
    "agent_type": "structural"
  }'
```

### Multi-Agent Workflow
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "message": "Design a complete building structure with cost analysis",
    "multi_agent": true,
    "agents": ["structural", "bom", "compliance"]
  }'
```

## 🎯 Example Queries

Try these example queries to test different agents:

### Structural Engineering
- "Design a steel beam for 12m span with 75kN/m load"
- "Calculate column sizing for 500kN axial load"
- "Check deflection for existing beam"

### Civil Engineering
- "Plan site layout for 5000sqm industrial complex"
- "Design drainage for parking lot"
- "Calculate earthwork volumes"

### Electrical Engineering
- "Design electrical layout for 200sqm office"
- "Calculate load requirements for warehouse"
- "Size cables for 100kW motor"

### Mechanical Engineering
- "Design assembly for rotating mechanism"
- "Analyze tolerance stack-up"
- "Select materials for high-temperature application"

### Multi-Disciplinary
- "Design a complete building with all MEP systems"
- "Generate BOM and cost estimate for structure"
- "Check code compliance for foundation design"

## 🏗️ Project Structure

```
ai-design-suite/
├── agents/                    # 15 specialized design agents
├── services/                  # Core services (LLM, CAD, etc.)
├── utils/                     # Utilities and prompt templates
├── tests/                     # Test suite
├── app.py                     # Main application
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container deployment
└── README.md                  # Full documentation
```

## 📖 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Try Different Agents**: Use the `/api/v1/agents` endpoint to see all capabilities
3. **Upload Files**: Use the `/api/v1/upload` endpoint for CAD files
4. **Multi-Agent Workflows**: Set `multi_agent: true` for complex projects
5. **Customize Prompts**: Edit `utils/prompts.py` for specialized guidance

## 🔧 Development

For development and customization:

1. **Install in Development Mode**:
```bash
pip install -e .
```

2. **Run Tests**:
```bash
pytest tests/ -v
python test_quick.py
```

3. **Add New Agents**: Follow the pattern in `agents/base_agent.py`

4. **Customize Prompts**: Edit templates in `utils/prompts.py`

## 🐳 Docker Deployment

```bash
# Build image
docker build -t ai-design-suite .

# Run container
docker run -p 8000:8000 -e LLM_PROVIDER=mock ai-design-suite
```

## 🎉 You're Ready!

The AI Design Suite is now fully operational. Start with simple queries and gradually explore the advanced multi-agent capabilities for complex engineering projects.