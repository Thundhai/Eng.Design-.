# Installation Guide for AI Design Suite

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Virtual environment support

## Step-by-Step Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Thundhai/ai-design-suite.git
cd ai-design-suite
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### Step 3: Install Core Dependencies ✅

```bash
# Install core AI Design Suite (WORKING!)
pip install --pre -r requirements.txt
```

**Note**: The `--pre` flag is required because the Microsoft Agent Framework is in preview.

### Step 4: Install Optional Features

#### Basic Optional Features (Recommended)

```bash
# Install file processing, CAD support, and basic features
pip install -r requirements-basic-optional.txt
```

This includes:
- ✅ DXF file support (`ezdxf`)
- ✅ Scientific computing (`scipy`)
- ✅ Excel/Word/PDF processing (`openpyxl`, `python-docx`, `reportlab`)
- ✅ Image processing (`Pillow`)
- ✅ Text-to-speech (`pyttsx3`)

#### Advanced CAD Features (Optional)

For advanced 3D CAD functionality:

**Option A: FreeCAD Integration**
```bash
# 1. Download and install FreeCAD from https://www.freecadweb.org/
# 2. Install system-wide (add to PATH)
# 3. Test installation:
python -c "import FreeCAD; print('FreeCAD available')"
```

**Option B: Conda Environment (Recommended for Advanced Features)**
```bash
# Create conda environment with CAD libraries
conda create -n ai-design-cad python=3.11
conda activate ai-design-cad
conda install -c conda-forge pythonocc-core ifcopenshell

# Install AI Design Suite in conda environment
pip install --pre -r requirements.txt
pip install -r requirements-basic-optional.txt
```

### Step 5: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# For basic usage, the default mock configuration works
```

### Step 6: Verify Installation

```bash
# Test basic functionality
python app.py --help

# Test with a simple query
python app.py --message "Hello, can you help with structural design?" --agent structural

# Start web server
python app.py --port 8000
# Open http://localhost:8000/docs for API documentation
```

## Alternative: Docker Installation

If you prefer Docker (includes all dependencies):

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Troubleshooting

### Common Issues

#### 1. Agent Framework Installation Error
```
ERROR: Could not find a version that satisfies the requirement agent-framework-azure-ai>=0.1.0
```
**Solution**: Use the `--pre` flag:
```bash
pip install --pre -r requirements.txt
```

#### 2. FreeCAD Import Error
```
ModuleNotFoundError: No module named 'FreeCAD'
```
**Solution**: 
- Download FreeCAD from official website
- Install system-wide (not via pip)
- Ensure FreeCAD is in system PATH

#### 3. CAD Library Compilation Errors
```
ERROR: Failed building wheel for pythonOCC-core
```
**Solution**: Use conda instead:
```bash
conda install -c conda-forge pythonocc-core
```

#### 4. Windows Build Tools Required
```
Microsoft Visual C++ 14.0 is required
```
**Solution**: 
- Install Visual Studio Build Tools
- Or use conda for complex packages
- Or skip advanced CAD features (basic functionality still works)

### What Works Without Optional Dependencies

The AI Design Suite core functionality works perfectly without any optional dependencies:
- ✅ All 15 AI agents
- ✅ Multi-agent workflows
- ✅ API server and CLI
- ✅ Docker deployment
- ✅ Mock CAD operations
- ✅ Basic file processing

## Testing Your Installation

### Quick Test
```bash
# Test CLI
python app.py --cli

# In interactive mode, try:
# "Design a simple beam structure"
# "Generate BOM for the project"
# "Analyze sustainability metrics"
```

### Full Test Suite
```bash
# Run automated tests
python test_quick.py
python test_automated_workflow.py

# Run with pytest
pytest tests/
```

### Web Interface Test
```bash
# Start server
python app.py --port 8000

# Open browser to:
# http://localhost:8000/docs (API documentation)
# http://localhost:8000/health (health check)
```

## Next Steps

1. ✅ **Basic Usage**: Try the examples in `QUICKSTART.md`
2. ✅ **API Integration**: Explore `/docs` endpoint for API usage
3. ✅ **Custom Agents**: Read `CONTRIBUTING.md` for development
4. ✅ **Production**: See `CONTAINER_DEPLOYMENT.md` for deployment

## Support

- 📚 Documentation: See `README.md` and other guides
- 🐛 Issues: Report on GitHub Issues
- 💬 Discussions: GitHub Discussions
- 🔧 Development: See `CONTRIBUTING.md`

The AI Design Suite is designed to work out-of-the-box with minimal setup! 🚀