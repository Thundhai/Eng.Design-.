#!/usr/bin/env python3
"""
AI Design Suite Launcher
Provides easy startup options for the AI Design Suite
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        # Don't check for agent_framework as it's optional with mock fallback
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment is properly configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Creating from example...")
        example_file = Path(".env.example")
        if example_file.exists():
            example_file.read_text().replace(example_file.name, env_file.name)
            with open(env_file, 'w') as f:
                f.write(example_file.read_text())
            print("✅ Created .env file")
        else:
            print("💡 Create .env file with your LLM provider settings")

def run_web_server(host="localhost", port=8000):
    """Launch the web server"""
    import socket
    
    # Check if port is available
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return True
            except OSError:
                return False
    
    # Find available port
    original_port = port
    while not is_port_available(port) and port < 8010:
        port += 1
    
    if port != original_port:
        print(f"⚠️  Port {original_port} is busy, using port {port} instead")
    
    print(f"🚀 Starting AI Design Suite web server at http://{host}:{port}")
    print(f"📚 API docs will be available at http://{host}:{port}/docs")
    
    try:
        cmd = [sys.executable, "app.py", "--host", host, "--port", str(port)]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")

def run_cli():
    """Launch the CLI interface"""
    print("🤖 Starting AI Design Suite CLI interface")
    try:
        cmd = [sys.executable, "app.py", "--cli"]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Exiting CLI...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting CLI: {e}")

def run_test():
    """Run quick validation test"""
    print("🧪 Running validation tests...")
    try:
        cmd = [sys.executable, "test_quick.py"]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("✅ All tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)

def show_status():
    """Show system status and available agents"""
    print("📊 AI Design Suite Status")
    print("=" * 40)
    
    # Check if in correct directory
    if not Path("app.py").exists():
        print("❌ Not in AI Design Suite directory")
        return
    
    print("✅ In AI Design Suite directory")
    
    # Check dependencies
    if check_dependencies():
        print("✅ Dependencies installed")
    
    # Check environment
    check_environment()
    
    # Show available agents
    print(f"\n🤖 Available Agents (15):")
    agents = [
        "root", "design_copilot", "civil_design", "structural_design",
        "mechanical_design", "electrical_design", "interior_design",
        "bom", "compliance", "drawing_qa", "sustainability",
        "generative_design", "report", "voice", "reflective"
    ]
    for agent in agents:
        print(f"   • {agent}")
    
    print("\n💡 Quick commands:")
    print("   python launch.py web       # Start web server")
    print("   python launch.py cli       # Start CLI")
    print("   python launch.py test      # Run tests")

def main():
    parser = argparse.ArgumentParser(description="AI Design Suite Launcher")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["web", "cli", "test", "status"],
                       help="Command to run")
    parser.add_argument("--host", default="localhost",
                       help="Host for web server (default: localhost)")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port for web server (default: 8000)")
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    if args.command == "web":
        if check_dependencies():
            run_web_server(args.host, args.port)
    elif args.command == "cli":
        if check_dependencies():
            run_cli()
    elif args.command == "test":
        if check_dependencies():
            run_test()
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()