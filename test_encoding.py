#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编码问题
"""
import sys
import os

print("=" * 60)
print("测试编码环境")
print("=" * 60)

print(f"\n1. 默认编码:")
print(f"  sys.getdefaultencoding(): {sys.getdefaultencoding()}")
print(f"  sys.getfilesystemencoding(): {sys.getfilesystemencoding()}")
print(f"  sys.stdout.encoding: {sys.stdout.encoding}")
print(f"  sys.stderr.encoding: {sys.stderr.encoding}")

print(f"\n2. 测试中文字符串:")
test_str = "你好，世界！Hello 世界！🐕✨"
print(f"  原始字符串：{test_str}")
print(f"  长度：{len(test_str)}")

print(f"\n3. 测试编码/解码:")
try:
    # UTF-8 编码
    utf8_bytes = test_str.encode('utf-8')
    print(f"  UTF-8 编码：{utf8_bytes}")
    print(f"  UTF-8 长度：{len(utf8_bytes)}")
    
    # UTF-8 解码
    utf8_decoded = utf8_bytes.decode('utf-8')
    print(f"  UTF-8 解码：{utf8_decoded}")
    
    # GBK 编码（Windows 默认）
    try:
        gbk_bytes = test_str.encode('gbk')
        print(f"  GBK 编码：{gbk_bytes}")
    except Exception as e:
        print(f"  GBK 编码失败：{e}")
        
except Exception as e:
    print(f"  编码测试失败：{e}")

print(f"\n4. 测试文件写入:")
test_file = "test_utf8.txt"
try:
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_str)
    print(f"  写入成功：{test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"  读取内容：{content}")
    
    os.remove(test_file)
    print(f"  清理文件：{test_file}")
except Exception as e:
    print(f"  文件测试失败：{e}")

print(f"\n5. 测试 JSON 编码:")
try:
    import json
    data = {"message": test_str, "status": "success"}
    json_str = json.dumps(data, ensure_ascii=False)
    print(f"  JSON 字符串：{json_str}")
    
    # 测试字节
    json_bytes = json_str.encode('utf-8')
    print(f"  JSON 字节：{json_bytes}")
    
    # 测试解码
    json_decoded = json_bytes.decode('utf-8')
    print(f"  JSON 解码：{json_decoded}")
    
except Exception as e:
    print(f"  JSON 测试失败：{e}")

print("\n" + "=" * 60)
print("编码测试完成")
print("=" * 60)
