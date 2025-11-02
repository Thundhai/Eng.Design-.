# 🚀 AI Design Suite - How to Run Outside VS Code

This guide shows you how to run and test the AI Design Suite project using command line tools like PowerShell or cmd.

## ✅ Prerequisites

1. **Python 3.9-3.14** installed on your system
2. **Git** (optional, for cloning from GitHub)
3. **Internet connection** for package installation

## 📁 Project Setup

### Option 1: Clone from GitHub
```powershell
git clone https://github.com/Thundhai/ai-design-suite.git
cd ai-design-suite
```

### Option 2: Use existing local copy
```powershell
cd C:\Users\Admin\ai-design-suite
```

## 🔧 Environment Setup

### 1. Create Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\activate

# You should see (.venv) in your prompt
```

### 2. Install Dependencies
```powershell
# Update pip first
python -m pip install --upgrade pip

# Install compatible redisvl first (for Python 3.14)
pip install redisvl==0.3.6

# Install agent framework with --pre flag
pip install agent-framework-azure-ai==1.0.0b251016 --pre

# Install all remaining dependencies
pip install -r requirements.txt
```

## 🚀 Running the Application

### Web Server Mode (Recommended)

```powershell
# Start the web server on default port 8000
python app.py

# Or specify a different port if 8000 is busy
python app.py --port 8002

# You'll see output like:
# 🚀 Starting AI Design Suite Web Server...
# 📖 API Documentation: http://0.0.0.0:8002/docs
# 🎯 Health Check: http://0.0.0.0:8002/health
# INFO: Uvicorn running on http://0.0.0.0:8002
```

**Access Points:**
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health
- **Interactive API**: Use the `/docs` page to test all endpoints

### Command Line Interface Mode

```powershell
# Interactive CLI mode
python app.py --cli

# Direct command execution
python app.py --message "Design a steel beam for 10m span" --agent structural

# Multi-agent workflow
python app.py --message "Complete building design with MEP systems" --agent root

# BOM and cost estimation
python app.py --message "Generate BOM and cost estimate" --agent bom
```

## 🧪 Testing the System

### 1. Run All Tests
```powershell
# Run the complete test suite
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=agents --cov-report=html

# Run specific test files
python -m pytest tests/test_integration.py -v
```

### 2. Quick Health Check
```powershell
python -c "
import asyncio
import sys
sys.path.append('.')
from agents.root_agent import RootAgent
from services.llm.llm_client import MockLLMClient

async def test():
    meta = {'llm_client': MockLLMClient(['Test response']), 'asset_registry': {}, 'config': {}}
    agent = RootAgent('test', meta)
    result = await agent.run({'message': 'Test message'})
    print('✅ System working:', result['status'])

asyncio.run(test())
"
```

## 🎯 Available Agents

Test individual agents with these commands:

```powershell
# Structural Engineering
python app.py --message "Design a steel beam for 15m span with 120kN load" --agent structural

# Electrical Systems
python app.py --message "Design electrical wiring layout for office building" --agent electrical

# Interior Design
python app.py --message "Create interior space layout for modern office" --agent interior

# Mechanical Systems
python app.py --message "Design HVAC system for 500m² building" --agent mechanical

# Generative Design
python app.py --message "Generate 5 design variations for the beam" --agent generative

# Project Planning
python app.py --message "Create construction schedule for the project" --agent planning

# Sustainability Analysis
python app.py --message "Analyze carbon footprint and sustainability metrics" --agent sustainability

# Code Compliance
python app.py --message "Check building code compliance for the design" --agent compliance

# Bill of Materials
python app.py --message "Generate detailed BOM with cost estimates" --agent bom

# Root Agent (Multi-Agent Orchestration)
python app.py --message "Complete comprehensive building design with all systems" --agent root
```

## 🌐 API Testing

When the web server is running, test with HTTP requests:

### Using PowerShell (Invoke-RestMethod)
```powershell
$body = @{
    message = "Design a steel beam for 10m span"
    agent = "structural"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8002/chat" -Method POST -Body $body -ContentType "application/json"
```

### Using curl (if available)
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Design a steel beam","agent":"structural"}'
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use
```powershell
# Check what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <process_id> /F

# Or use a different port
python app.py --port 8003
```

#### 2. Import Errors
```powershell
# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test imports
python -c "from agents.root_agent import RootAgent; print('✅ Imports working')"
```

#### 3. Dependency Conflicts
```powershell
# Clean install
pip uninstall agent-framework agent-framework-azure-ai agent-framework-redis -y
pip install redisvl==0.3.6
pip install agent-framework-azure-ai==1.0.0b251016 --pre
pip install -r requirements.txt
```

#### 4. Python Version Issues
- The project works best with Python 3.9-3.14
- If using Python 3.14, make sure you have the compatible redisvl version (0.3.6)

### Environment Configuration

Create a `.env` file in the project root for custom settings:
```env
LLM_PROVIDER=mock
DEBUG=true
PORT=8002
LOG_LEVEL=INFO
```

## 📊 Performance Testing

```powershell
# Time a complex operation
Measure-Command { 
    python app.py --message "Complete building design with all systems" --agent root 
}

# Check system resources
Get-Process python | Select-Object CPU, WorkingSet, ProcessName
```

## 🐳 Docker Alternative

If you prefer containerized deployment:

```powershell
# Build Docker image
docker build -t ai-design-suite:latest .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📝 Quick Start Checklist

- [ ] Navigate to project directory
- [ ] Activate virtual environment
- [ ] Install dependencies
- [ ] Test installation: `python -m pytest tests/ -v`
- [ ] Start web server: `python app.py --port 8002`
- [ ] Open browser: http://localhost:8002/docs
- [ ] Test API endpoints

## 🎯 Success Indicators

You know everything is working when:
- ✅ No deprecation warnings on startup
- ✅ All tests pass (18/18)
- ✅ Web server starts without errors
- ✅ API documentation loads at /docs
- ✅ Health check returns "healthy" status
- ✅ Individual agents respond correctly

## 🆘 Getting Help

If you encounter issues:
1. Check this troubleshooting guide
2. Verify all dependencies are installed correctly
3. Ensure you're using a compatible Python version
4. Check the GitHub repository for updates
5. Review the error logs for specific issues

**GitHub Repository**: https://github.com/Thundhai/ai-design-suite

---

Happy building with AI Design Suite! 🏗️✨
</content>
</invoke>