#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dogeAgent CLI Chat - 命令行聊天界面
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from agent.factory import get_agent
from storage.session_store import session_store
from agent.emotion_engine import EmotionEngine

print("=" * 60)
print("       dogeAgent CLI Chat")
print("=" * 60)

# Initialize
print("\nInitializing...")
agent = get_agent()
engine = EmotionEngine("user")
print(f"Agent: {agent.provider}")
print(f"Greeting: {engine.get_greeting()}")
print("\nType 'quit' or 'exit' to exit")
print("=" * 60)

# Chat loop
while True:
    try:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Doge: Bye! See you next time!")
            break
        
        # Get response from agent
        print("Doge is typing...", end='', flush=True)
        response = agent.chat(user_input)
        
        # Update emotion
        engine.add_intimacy(0.1, reason="chat")
        
        print(f"\nDoge: {response}")
        
    except KeyboardInterrupt:
        print("\n\nBye!")
        break
    except Exception as e:
        print(f"\nError: {e}")
        break
