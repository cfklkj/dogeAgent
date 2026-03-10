#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试历史消息格式
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing history format...")
print("=" * 60)

from storage.session_store import session_store

# Clear old history
print("\n1. Clearing old history...")
session_store.clear_history("test_user")
print("   History cleared")

# Add test messages
print("\n2. Adding test messages...")
session_store.add_message("human", "你好", "test_user")
session_store.add_message("ai", "你好！我是 Doge", "test_user")
print("   Messages added")

# Get history
print("\n3. Getting history...")
history_dicts = session_store.get_history("test_user", limit=10)
print(f"   Type: {type(history_dicts)}")
print(f"   Length: {len(history_dicts)}")
print(f"   Content: {history_dicts}")

# Convert to tuples
print("\n4. Converting to tuples...")
history = [
    (item.get('role', ''), item.get('content', ''))
    for item in history_dicts
    if isinstance(item, dict) and 'role' in item and 'content' in item
]
print(f"   Type: {type(history)}")
print(f"   Length: {len(history)}")
print(f"   Content: {history}")

# Test with agent
print("\n5. Testing with agent...")
try:
    from agent.factory import get_agent
    agent = get_agent()
    
    # Test with empty history
    print("\n6. Testing with empty history...")
    response = agent.chat("测试", [])
    print(f"   Empty history response: {response[:50]}...")
    
    # Test with history
    print("\n7. Testing with history...")
    response = agent.chat("今天天气怎么样", history)
    print(f"   With history response: {response[:50]}...")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
