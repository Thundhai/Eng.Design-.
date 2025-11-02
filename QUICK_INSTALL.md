# Quick Installation Guide

## ✅ Working Installation Commands

### Core Installation (Required)
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install AI Design Suite (WORKING!)
pip install --pre -r requirements.txt
```

### Optional Features (Recommended)
```bash
# Install file processing, CAD support, text-to-speech
pip install -r requirements-basic-optional.txt
```

### Docker (All-in-One)
```bash
# Run with all dependencies included
docker-compose up -d
# Access at http://localhost:8000
```

## ✅ Verified Working Packages

### Core Framework (Beta)
- ✅ `agent-framework-azure-ai==1.0.0b251028` 
- ✅ `azure-ai-inference==1.0.0b9`

### Web Framework  
- ✅ `fastapi>=0.104.0`
- ✅ `uvicorn[standard]>=0.24.0`

### Optional Features
- ✅ `ezdxf>=1.0.0` (DXF CAD files)
- ✅ `scipy>=1.10.0` (Engineering calculations)
- ✅ `openpyxl>=3.1.0` (Excel files)
- ✅ `python-docx>=0.8.11` (Word documents)  
- ✅ `reportlab>=4.0.0` (PDF generation)
- ✅ `Pillow>=10.0.0` (Image processing)
- ✅ `pyttsx3>=2.90` (Text-to-speech)

## ✅ Test Your Installation

```bash
# Test basic functionality
python app.py --help

# Test with a simple query
python app.py --message "Design a simple beam" --agent structural

# Start web server
python app.py --port 8000
# Open http://localhost:8000/docs
```

## 🚀 Ready for Development

The AI Design Suite is now fully functional with:
- 15 specialized AI agents
- Multi-agent workflows  
- API server with documentation
- CLI interface
- Docker deployment
- File processing capabilities
- Basic CAD support

No more installation issues! 🎉