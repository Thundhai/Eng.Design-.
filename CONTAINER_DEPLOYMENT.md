# AI Design Suite - Container Deployment Guide

## 🚀 Container Overview

The AI Design Suite is now fully containerized with a production-ready Docker setup that includes:

- **Multi-stage Docker build** for optimized image size and security
- **Non-root user execution** for enhanced security  
- **Health checks** for monitoring container status
- **Persistent storage** for outputs, sessions, and logs
- **Docker Compose** for easy deployment and orchestration

## 📋 Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose v2.0+
- 4GB+ RAM recommended
- 2GB+ disk space for images and data

## 🛠️ Build & Deployment Options

### Option 1: Docker Compose (Recommended)

The easiest way to deploy the AI Design Suite:

```bash
# Clone or navigate to the AI Design Suite directory
cd ai-design-suite

# Start the application (builds automatically if needed)
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop the application
docker compose down
```

### Option 2: Manual Docker Build & Run

For custom configurations:

```bash
# Build the image
docker build -t ai-design-suite:latest .

# Run the container
docker run -d \
  --name ai-design-suite \
  -p 8003:8000 \
  -v ./outputs:/app/outputs \
  -v ./sessions:/app/sessions \
  -v ./logs:/app/logs \
  ai-design-suite:latest

# Check health
curl http://localhost:8003/health
```

## 🌐 Access & Testing

Once deployed, the AI Design Suite is available at:

- **Main Application**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/health

### Test API Endpoints

```bash
# Health check
curl http://localhost:8003/health

# API documentation (Swagger UI)
# Open http://localhost:8003/docs in browser

# Example agent request (via Swagger UI or direct API)
POST /api/v1/chat
{
  "message": "Design a steel beam for 30ft span",
  "agent_type": "structural",
  "session_id": "test-session"
}
```

## 🔧 Configuration

### Environment Variables

The container supports these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `production` | Deployment environment |
| `LLM_PROVIDER` | `mock` | LLM provider (mock/azure_ai_foundry) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Internal server port |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

### Persistent Storage

The container automatically creates and mounts these directories:

- `./outputs` - Generated files and reports
- `./sessions` - User session data
- `./logs` - Application logs

## 🏥 Health Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8003/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-02T02:20:53.936002+00:00",
  "version": "1.0.0",
  "llm_provider": "mock",
  "initialized": true
}
```

### Container Health Status

```bash
# Check container health
docker compose ps

# View health check logs
docker compose logs ai-design-suite
```

## 🔒 Security Features

- **Non-root execution**: Container runs as `aidesign` user
- **Minimal attack surface**: Multi-stage build with production-only dependencies
- **Security headers**: FastAPI security middleware enabled
- **Resource limits**: Container resource constraints can be configured

## 📊 Agent Capabilities in Container

The containerized version includes all 15+ specialized agents:

### 🏗️ **Engineering Agents**
- **Civil Design Agent** - Site analysis and foundation design
- **Structural Design Agent** - Beam, column, and foundation calculations
- **Mechanical Design Agent** - Assembly design and tolerance analysis
- **Electrical Design Agent** - Power distribution and circuit design
- **Interior Design Agent** - Space planning and layout optimization

### 🔧 **Analysis & Optimization Agents**
- **BOM Agent** - Material lists and cost estimation
- **Compliance Agent** - Building code and regulatory compliance
- **Drawing QA Agent** - Quality control and clash detection
- **Sustainability Agent** - Environmental impact and LCA analysis
- **Generative Design Agent** - AI-powered design optimization

### 🚀 **Advanced Workflow Agents**
- **⭐ Planning Engineer Agent** - Construction scheduling and resource optimization
- **Automated Workflow Agent** - Multi-agent coordination and orchestration
- **Root Agent** - Intelligent request routing and session management

## 🔄 Automated Workflows

The container supports fully automated multi-agent workflows:

```bash
# Example: Complete building design workflow
curl -X POST http://localhost:8003/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Complete comprehensive design for 5-story office building with MEP systems and construction planning",
    "agent_type": "root",
    "session_id": "workflow-session"
  }'
```

This automatically triggers 10+ agents in the correct sequence:
1. Civil → Structural → MEP Systems
2. BOM → Compliance → QA
3. Sustainability → Planning Engineer
4. Final coordination and delivery

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8004:8000"  # Use different external port
   ```

2. **Container won't start**
   ```bash
   # Check logs
   docker compose logs
   
   # Rebuild if needed
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

3. **Health check fails**
   ```bash
   # Check internal connectivity
   docker compose exec ai-design-suite curl localhost:8000/health
   ```

### Performance Optimization

- **Memory**: Allocate 4GB+ RAM for complex workflows
- **CPU**: Multi-core recommended for parallel agent execution
- **Storage**: SSD recommended for faster file I/O

## 🚀 Production Deployment

### Scaling Options

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  ai-design-suite:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'
```

### Reverse Proxy Setup

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📚 Additional Resources

- **API Documentation**: Available at `/docs` endpoint
- **Agent Documentation**: See individual agent files in `/agents/`
- **Workflow Examples**: Check `/tests/` directory
- **Configuration**: Review `.env.example` for all options

## 🎯 Next Steps

1. **Access the application** at http://localhost:8003
2. **Explore the API** documentation at http://localhost:8003/docs
3. **Test individual agents** or automated workflows
4. **Configure LLM providers** for enhanced capabilities
5. **Set up monitoring** and logging for production use

The AI Design Suite is now ready for comprehensive engineering design automation! 🚀