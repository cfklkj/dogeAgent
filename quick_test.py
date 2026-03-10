#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dogeAgent Quick Test
"""
import sys
import os
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("       dogeAgent Quick Functionality Test")
print("=" * 60)

# Test 1: Config
print("\n[TEST 1] Configuration...")
try:
    from config.settings import APP_NAME, APP_VERSION, DATA_DIR
    print(f"  App: {APP_NAME} v{APP_VERSION}")
    print(f"  Data Dir: {DATA_DIR}")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Test 2: Models
print("\n[TEST 2] Model Configuration...")
try:
    from models.config import MODEL_CONFIG
    print(f"  Providers: {list(MODEL_CONFIG.keys())}")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Test 3: Tools
print("\n[TEST 3] Tools...")
try:
    from tools import get_all_tools
    tools = get_all_tools()
    print(f"  Tools: {[t.name for t in tools]}")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Test 4: Storage
print("\n[TEST 4] Storage...")
try:
    from storage.session_store import session_store
    session_store.save_preference("test_key", "test_value")
    value = session_store.get_preference("test_key")
    assert value == "test_value", "Storage mismatch"
    print("  Database: OK")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Test 5: Emotion Engine
print("\n[TEST 5] Emotion Engine...")
try:
    from agent.emotion_engine import EmotionEngine, Emotion
    engine = EmotionEngine("test_user")
    greeting = engine.get_greeting()
    intimacy_text = engine.get_intimacy_level_text()
    print(f"  Greeting: {greeting[:30]}...")
    print(f"  Intimacy: {intimacy_text}")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Test 6: Weather
print("\n[TEST 6] Weather Module...")
try:
    from weather import WeatherManager
    weather = WeatherManager()
    print("  Weather module loaded")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Test 7: Search
print("\n[TEST 7] Search Module...")
try:
    from search import SearchManager
    search = SearchManager()
    print("  Search module loaded")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Test 8: Plugin System
print("\n[TEST 8] Plugin System...")
try:
    from plugins.plugin_manager import PluginManager
    pm = PluginManager()
    print("  Plugin manager initialized")
    print("  [PASS]")
except Exception as e:
    print(f"  [FAIL]: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("  ALL TESTS PASSED!")
print("=" * 60)
print("\nNext: Configure NVIDIA_API_KEY in .env, then run: python start.py")
