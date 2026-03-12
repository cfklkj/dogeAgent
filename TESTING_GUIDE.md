# 🧪 dogeAgent 币圈功能测试指南

**更新时间**: 2026-03-11 16:30  
**状态**: ✅ 工具已修复，需重启应用

---

## 🚨 重要提示

**工具注册已修复**，但需要**重启 dogeAgent** 才能生效！

---

## 📋 测试步骤

### 步骤 1: 关闭现有 dogeAgent

在任务栏找到狗子图标，右键 → 退出  
或者运行：
```bash
taskkill /F /IM electron.exe
```

### 步骤 2: 重新启动 dogeAgent

**方式 A - 使用重启脚本（推荐）**:
```bash
cd H:\openclawWk\workspace-magic\workspace\2026\03\10\dogeAgent
restart_and_test.bat
```

**方式 B - 手动启动**:
```bash
cd H:\openclawWk\workspace-magic\workspace\2026\03\10\dogeAgent
npm start
```

### 步骤 3: 验证工具加载

启动后，查看日志中是否显示：
```
工具初始化完成，共 6 个工具
  - 加密货币工具：2 个
```

### 步骤 4: 在聊天框测试

双击狗子打开聊天窗口，输入以下指令：

#### 测试 1: 查价格
```
BTC 什么价格
```
**预期回复**:
> BTCUSDT: $69,528 (-1.8% 24h) | 高：$71,777 | 低：$69,266 | 成交量：$2.1B

#### 测试 2: 看分析
```
分析 ETH 走势
```
**预期回复**:
> 📊 ETHUSDT 分析 (1d)
> 当前价：$2,010
> 趋势：多头 (MA7>MA30)
> RSI: 53.4 (中性)
> 总结：...

#### 测试 3: DOGE 价格（彩蛋）
```
DOGE 价格
```
**预期回复**:
> DOGEUSDT: $0.XX (X%) ...

---

## 🔍 故障排查

### 问题 1: 回复仍然是通用介绍
**现象**: 输入 "BTC 什么价格"，回复 "我是 Doge，可以帮你..."  
**原因**: 工具未正确加载  
**解决**:
1. 完全关闭 dogeAgent（任务栏右键退出）
2. 删除 `__pycache__` 文件夹（如果有）
3. 重新启动

### 问题 2: 显示 "工具调用失败"
**原因**: API 访问问题  
**解决**: 检查网络连接，确保能访问 Binance API

### 问题 3: 没有反应
**原因**: Python 桥接未启动  
**解决**: 查看日志，确认 `bridge.py` 正常运行

---

## 📊 验证工具加载的快捷方法

运行测试脚本：
```bash
cd H:\openclawWk\workspace-magic\workspace\2026\03\10\dogeAgent
python test_final.py
```

应输出：
```
✅ 已注册 6 个工具:
  - get_current_time
  - get_current_date
  - calculate
  - get_weather
  - get_crypto_price     ← 必须有
  - analyze_crypto       ← 必须有
```

---

## ✅ 成功标准

| 测试项 | 预期行为 | 状态 |
|--------|---------|------|
| 工具数量 | 显示 6 个工具 | ⏳ 待验证 |
| BTC 价格 | 返回实时价格 | ⏳ 待验证 |
| ETH 分析 | 返回 RSI/MA/趋势 | ⏳ 待验证 |
| DOGE 价格 | 返回狗狗币价格 | ⏳ 待验证 |

---

## 🎯 下一步

测试通过后，可以：
1. 添加价格预警功能
2. 增加更多技术指标
3. 支持自定义币种列表

---

**维护者**: SuperAgent  
**创建日期**: 2026-03-11
