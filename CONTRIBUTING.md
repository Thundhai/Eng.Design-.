# Contributing to AI Design Suite

Thank you for your interest in contributing to the AI Design Suite! This document provides guidelines for contributing to the project.

## Code of Conduct

Please be respectful and professional in all interactions. We're building an inclusive community focused on advancing AI-powered engineering design.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites
- Python 3.8+
- Docker (optional, for containerized development)

### Installation
```bash
# Clone the repository
git clone https://github.com/Thundhai/ai-design-suite.git
cd ai-design-suite

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your settings

# Run the application
python app.py --cli
```

## Project Structure

```
ai-design-suite/
├── agents/              # Specialized AI agents
├── services/           # Core services (LLM, CAD)
├── utils/              # Utility functions
├── tests/              # Test suite
├── app.py              # Main application
└── requirements.txt    # Python dependencies
```

## Adding New Agents

When creating new specialized agents:

1. Inherit from `BaseAgent` class
2. Implement required methods (`process_request`, `get_capabilities`)
3. Add comprehensive docstrings
4. Include unit tests
5. Update the README with agent capabilities

## Testing

```bash
# Run quick tests
python test_quick.py

# Run automated workflow tests
python test_automated_workflow.py

# Run integration tests
python -m pytest tests/
```

## Docker Development

```bash
# Build container
docker build -t ai-design-suite:latest .

# Run with Docker Compose
docker-compose up -d
```

## Submitting Changes

1. Ensure all tests pass
2. Update documentation as needed
3. Follow the existing code style
4. Write clear commit messages
5. Submit a pull request with detailed description

## Areas for Contribution

- New specialized engineering agents
- CAD file format support
- Integration with external engineering tools
- Performance optimizations
- Documentation improvements
- Test coverage expansion

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing to the AI Design Suite!