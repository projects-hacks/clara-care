#!/usr/bin/env python3
"""
Quick Start Script for ClaraCare Backend
Verifies setup and provides next steps
"""

import os
import sys
from pathlib import Path


def check_env_vars():
    """Check required environment variables"""
    print("Checking environment variables...")
    
    required = {
        "DEEPGRAM_API_KEY": "Deepgram Voice Agent API key",
        "TWILIO_ACCOUNT_SID": "Twilio Account SID",
        "TWILIO_AUTH_TOKEN": "Twilio Auth Token",
        "TWILIO_PHONE_NUMBER": "Twilio Phone Number"
    }
    
    optional = {
        "YOUCOM_API_KEY": "You.com Search API key",
        "SANITY_PROJECT_ID": "Sanity CMS Project ID",
        "FOXIT_API_KEY": "Foxit Document Generation API key"
    }
    
    missing = []
    for var, description in required.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ✗ {var}: NOT SET")
            missing.append(f"{var} ({description})")
    
    if missing:
        print("\n⚠️  Missing required environment variables:")
        for item in missing:
            print(f"  - {item}")
        print("\nAdd these to your .env file")
        return False
    
    # Check optional vars
    print("\n  Optional variables:")
    for var, description in optional.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ⚠ {var}: NOT SET ({description})")
    
    return True


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required = ["fastapi", "uvicorn", "websockets", "httpx"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)
    
    if missing:
        print("\n⚠️  Missing packages:")
        for package in missing:
            print(f"  - {package}")
        print("\nRun: pip install -r requirements.txt")
        return False
    
    return True


def check_project_structure():
    """Verify project structure"""
    print("\nChecking project structure...")
    
    required_files = [
        "app/main.py",
        "app/voice/persona.py",
        "app/voice/agent.py",
        "app/voice/functions.py",
        "app/voice/twilio_bridge.py",
        "app/voice/outbound.py",
        "requirements.txt"
    ]
    
    backend_dir = Path(__file__).parent
    missing = []
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path}")
            missing.append(file_path)
    
    if missing:
        print("\n⚠️  Missing files - project structure incomplete")
        return False
    
    return True


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE - Ready to start Clara!")
    print("=" * 70)
    
    print("\n📋 Next Steps:\n")
    
    print("1. Start the server:")
    print("   $ cd backend")
    print("   $ PYTHONPATH=/Users/maverickrajeev/Documents/projects/clara-care/backend python3 -m app.main")
    print("   Server will run on http://localhost:8000\n")
    
    print("2. Test the components:")
    print("   $ python3 tests/test_voice.py\n")
    
    print("3. For local testing (optional):")
    print("   Clara can call patients via Twilio API - no ngrok needed for testing!")
    print("   $ curl -X POST \"http://localhost:8000/voice/call/patient?patient_id=demo&patient_phone=+1YOUR_NUMBER&patient_name=Test\"\n")
    
    print("4. For production deployment:")
    print("   Deploy to Replit (recommended) or use a cloud platform")
    print("   Update SERVER_PUBLIC_URL in .env with your public URL\n")
    
    print("5. Clara will call patients for daily check-ins! 📞\n")
    
    print("=" * 70)
    print("\n📚 Documentation: backend/README.md")
    print("🐛 Issues? Check logs and Twilio debugger")
    print("\n")


def main():
    """Run all checks"""
    print("=" * 70)
    print("ClaraCare Backend - Quick Start Check")
    print("=" * 70)
    print()
    
    # Load .env if it exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print(f"Loaded environment from: {env_file}\n")
    else:
        print("⚠️  No .env file found - using system environment variables\n")
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_vars)
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print_next_steps()
    else:
        print("❌ SETUP INCOMPLETE")
        print("=" * 70)
        print("\nFix the issues above and run this script again.")
        print("\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
