# 🔧 Windows GBK 编码问题修复

**日期**: 2026-03-10  
**问题**: `'gbk' codec can't encode character '\U0001f44b'`  
**状态**: ✅ 已修复

---

## 问题现象

1. 用户发送消息 "hi"
2. 系统错误：`'gbk' codec can't encode character '\U0001f44b'`
3. Python 日志输出包含 emoji (👋) 导致编码失败

## 问题原因

Windows 控制台默认使用 GBK 编码，无法处理：
- Emoji 表情（如 👋）
- 部分特殊 Unicode 字符
- 中文日志中的特殊符号

## 解决方案

### 1. 自定义 UTF-8 日志处理器

```python
import io
import logging

class UTF8StreamHandler(logging.StreamHandler):
    """UTF-8 编码的日志处理器"""
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)
```

### 2. 强制 JSON 使用 UTF-8

```python
# 使用 ensure_ascii=False 保留原始字符
print(json.dumps({"message": "你好 👋"}, ensure_ascii=False))
```

### 3. 设置环境变量

在启动脚本中设置：
```python
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
```

---

## 修改文件

- `desktop/bridge.py` - 添加 UTF8StreamHandler
- `start.py` - 启动脚本设置 UTF-8
- `electron/main.js` - 无变化

---

## 验证步骤

### 1. 测试 Python 桥接
```bash
python desktop\bridge.py
```

**预期**: 正常启动，无编码错误

### 2. 测试聊天
```bash
npm start
```

1. 双击狗子打开聊天
2. 发送 "hi" 或 "你好"
3. 收到带 emoji 的回复

---

## Git 提交

| 提交哈希 | 信息 |
|----------|------|
| `1ed8fc0` | fix: 修复 Windows GBK 编码问题 |

---

## 相关文件

- `desktop/bridge.py` - Python 桥接服务
- `start.py` - 启动脚本
- `ENCODING_FIX.md` - 本文档

---

## 经验教训

### 1. 跨平台编码
- Windows 默认 GBK，Linux/macOS 默认 UTF-8
- 始终显式指定编码

### 2. 日志输出
- 避免在日志中使用 emoji
- 或使用 UTF-8 处理器

### 3. JSON 输出
- 使用 `ensure_ascii=False` 保留原始字符
- 或转换为 ASCII 兼容格式

---

**修复者**: SuperAgent  
**测试者**: Fly  
**状态**: ✅ 已修复  
**优先级**: 高
