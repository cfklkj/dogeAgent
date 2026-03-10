#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Python 桥接服务
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Python Bridge...")
print("=" * 50)

# Test 1: Import modules
print("\n[1/3] Importing modules...")
try:
    from desktop.bridge import BridgeService
    print("  ✓ Bridge module imported")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize Bridge
print("\n[2/3] Initializing Bridge...")
try:
    bridge = BridgeService()
    print("  ✓ Bridge initialized")
except Exception as e:
    print(f"  ✗ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Test chat function
print("\n[3/3] Testing chat...")
try:
    result = bridge.chat("你好")
    print(f"  Result: {result}")
except Exception as e:
    print(f"  Note: {e}")

print("\n" + "=" * 50)
print("Bridge test completed!")
print("\nNext: Restart the app to apply changes")
