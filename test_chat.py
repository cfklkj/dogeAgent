#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试聊天功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing DogeAgent Chat Function")
print("=" * 60)

# Test 1: Import bridge
print("\n[1/4] Importing Bridge module...")
try:
    from desktop.bridge import BridgeService
    print("  [OK] Bridge module imported")
except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize Bridge
print("\n[2/4] Initializing Bridge Service...")
try:
    bridge = BridgeService()
    print("  [OK] Bridge Service initialized")
except Exception as e:
    print(f"  [FAIL] Initialization failed: {e}")
    sys.exit(1)

# Test 3: Initialize Agent
print("\n[3/4] Initializing Agent...")
try:
    result = bridge.init_agent()
    print(f"  Result: {result}")
    if result.get('status') == 'success':
        print("  [OK] Agent initialized successfully")
    else:
        print(f"  [WARN] Agent initialization issue: {result.get('message')}")
except Exception as e:
    print(f"  [FAIL] Agent initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Send a chat message
print("\n[4/4] Testing chat message...")
try:
    result = bridge.chat("ni hao")
    print(f"  Result: {result}")
    if result.get('status') == 'success':
        msg = result.get('message', '')
        print(f"  [OK] Chat successful: {msg[:50]}...")
    else:
        print(f"  [WARN] Chat issue: {result.get('message')}")
except Exception as e:
    print(f"  [FAIL] Chat failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
print("\nNext steps:")
print("1. If all tests passed, restart the app: npm start")
print("2. Open chat window by double-clicking the doge")
print("3. Send a message to test")
