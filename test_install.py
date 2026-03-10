#!/usr/bin/env python3
"""
dogeAgent 安装测试脚本
"""
import sys
import os

print("=" * 50)
print("dogeAgent Installation Test")
print("=" * 50)

# Test 1: Core modules
print("\n[1/5] Testing core modules...")
try:
    import langchain
    import langchain_nvidia_ai_endpoints
    from dotenv import load_dotenv
    print("    OK: Core modules loaded")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# Test 2: Load environment
print("\n[2/5] Loading environment...")
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
    print("    OK: Environment loaded")
else:
    print("    WARN: .env file not found, using defaults")

# Test 3: Check NVIDIA API Key
print("\n[3/5] Checking NVIDIA API Key...")
nvidia_key = os.getenv('NVIDIA_API_KEY')
if nvidia_key and nvidia_key != 'your_nvidia_api_key_here':
    print("    OK: NVIDIA API Key configured")
else:
    print("    WARN: NVIDIA API Key not set")
    print("    Get one at: https://build.nvidia.com/")

# Test 4: Import project modules
print("\n[4/5] Testing project modules...")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from config.settings import APP_NAME, APP_VERSION
    print(f"    OK: Config loaded - {APP_NAME} v{APP_VERSION}")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

# Test 5: Database initialization
print("\n[5/5] Testing database...")
try:
    from storage.session_store import session_store
    print("    OK: Database initialized")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("All tests passed!")
print("=" * 50)
print("\nNext steps:")
print("1. Configure NVIDIA API Key in .env")
print("2. Install Node.js dependencies: npm install")
print("3. Run: python start.py")
