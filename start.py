#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 设置 UTF-8 编码并启动应用
"""
import os
import sys
import subprocess

# 设置 Python 默认编码为 UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Windows 设置控制台编码
if sys.platform == 'win32':
    os.system('chcp 65001')

# 启动 Electron 应用
print("Starting dogeAgent...")
subprocess.run(['npm', 'start'], shell=True)
