#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dogeAgent 简化启动脚本 - 测试核心功能
"""
import sys
import os
import io
from pathlib import Path
from datetime import datetime

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("       dogeAgent Core Function Test")
print("=" * 60)

# 1. Load config
print("\n[1/6] Loading configuration...")
from config.settings import APP_NAME, APP_VERSION, NVIDIA_API_KEY
print(f"  App: {APP_NAME} v{APP_VERSION}")
if NVIDIA_API_KEY and NVIDIA_API_KEY != 'your_nvidia_api_key_here':
    print(f"  NVIDIA API Key: Configured [OK]")
    api_configured = True
else:
    print(f"  NVIDIA API Key: Not configured [WARN]")
    print("  Please edit .env file to add NVIDIA_API_KEY")
    api_configured = False

# 2. Initialize Agent
print("\n[2/6] Initializing Agent...")
try:
    from agent.factory import get_agent
    if api_configured:
        agent = get_agent()
        print(f"  Agent initialized [OK]")
        print(f"  Current provider: {agent.provider}")
    else:
        print(f"  Skip (API key not configured)")
        agent = None
except Exception as e:
    print(f"  Agent init failed: {e}")
    agent = None

# 3. Test tools
print("\n[3/6] Testing tools...")
from tools import get_current_time, get_current_date, calculate
# Direct function calls
print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
print(f"  Date: {datetime.now().strftime('%Y-%m-%d')}")
print(f"  Calc: {calculate.func('2+2*3')}")

# 4. Test emotion engine
print("\n[4/6] Testing emotion engine...")
from agent.emotion_engine import EmotionEngine
engine = EmotionEngine("test_user")
greeting = engine.get_greeting()
print(f"  Greeting: {greeting}")
print(f"  Intimacy: {engine.intimacy_level} ({engine.get_intimacy_level_text()})")

# 5. Test weather
print("\n[5/6] Testing weather module...")
from weather import WeatherManager
import asyncio
weather = WeatherManager()
weather_text = asyncio.run(weather.get_weather("Beijing"))
print(f"  Weather: {weather_text[:60]}...")

# 6. Test storage
print("\n[6/6] Testing storage...")
from storage.session_store import session_store
session_store.add_message("human", "Hello, this is a test")
history = session_store.get_history(limit=1)
print(f"  Messages: {len(history)} saved")
if history:
    print(f"  Latest: {history[0]['content']}")

print("\n" + "=" * 60)
print("Core function test completed!")
print("=" * 60)
print("\nNext steps:")
if not api_configured:
    print("  1. Configure NVIDIA_API_KEY in .env file")
    print("  2. Run this script again")
if agent:
    print("  1. Try chatting: agent.chat('你好')")
    print("  2. Install Electron for GUI (optional)")
    print("  3. Or build a simple CLI interface")
