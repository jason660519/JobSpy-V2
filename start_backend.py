#!/usr/bin/env python3
"""
Simple script to start JobSpy v2 backend without Docker
"""
import sys
import subprocess
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    requirements = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy[asyncio]>=2.0.23",
        "asyncpg>=0.29.0",
        "redis>=5.0.1",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "httpx>=0.25.2",
        "openai>=1.3.7",
        "structlog>=23.2.0",
        "python-dotenv>=1.0.0"
    ]
    
    print("Installing required packages...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your API keys")
        return False
    print("✅ .env file found")
    return True

def start_backend():
    """Start the FastAPI backend"""
    if not check_env_file():
        return
    
    print("Starting JobSpy v2 Backend...")
    print("📡 Backend will be available at: http://localhost:8000")
    print("📖 API Documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        # Change to backend directory
        backend_dir = Path("backend")
        if backend_dir.exists():
            os.chdir(backend_dir)
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

if __name__ == "__main__":
    print("🚀 JobSpy v2 Backend Starter")
    print("=" * 40)
    
    install_requirements()
    start_backend()