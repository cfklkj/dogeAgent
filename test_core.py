#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试核心文件加载
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Core Files Loading")
print("=" * 60)

# Test 1: Import core loader
print("\n[1/4] Importing core loader...")
try:
    from core.core_loader import CoreLoader, get_core_loader
    print("  [OK] Core loader imported")
except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Initialize core loader
print("\n[2/4] Initializing core loader...")
try:
    loader = get_core_loader()
    print("  [OK] Core loader initialized")
except Exception as e:
    print(f"  [FAIL] Initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Load core files
print("\n[3/4] Loading core files...")
try:
    loader.load_all()
    print(f"  [OK] SOUL.md loaded: {len(loader.soul)} sections")
    print(f"  [OK] IDENTITY.md loaded: {len(loader.identity)} sections")
    print(f"  [OK] MEMORY.md loaded: {len(loader.memory)} sections")
    print(f"  [OK] COLLABORATION.md loaded: {len(loader.collaboration)} sections")
    print(f"  [OK] TOOLS.md loaded: {len(loader.tools)} sections")
except Exception as e:
    print(f"  [FAIL] Loading failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Get system prompt
print("\n[4/4] Getting system prompt...")
try:
    prompt = loader.get_system_prompt()
    print(f"  [OK] System prompt generated ({len(prompt)} chars)")
    print(f"  Preview: {prompt[:100]}...")
except Exception as e:
    print(f"  [FAIL] Failed to get prompt: {e}")

print("\n" + "=" * 60)
print("Core files test completed!")
print("=" * 60)
print("\nNext steps:")
print("1. Restart the application: npm start")
print("2. Test with weather queries")
print("3. Verify personality and communication style")
