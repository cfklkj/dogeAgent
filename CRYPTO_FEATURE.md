# 🐶 dogeAgent 币圈行情功能使用说明

**版本**: v1.0 (中策方案)  
**完成时间**: 2026-03-11  
**状态**: ✅ 已完成并测试通过

---

## 🎯 功能清单

### 已实现功能
- ✅ 实时价格查询（Binance API）
- ✅ 24 小时涨跌幅统计
- ✅ 高/低价、成交量
- ✅ RSI 技术指标计算
- ✅ MA 均线（7 日/30 日）
- ✅ 趋势分析（多头/空头/震荡）
- ✅ 自然语言解读

### 数据来源
- **价格数据**: Binance API (无需 API Key)
- **技术指标**: 本地计算（基于 K 线数据）
- **更新频率**: 实时（每次查询获取最新数据）

---

## 🚀 使用方法

### 方式 1: 直接调用工具

```python
# 1. 查询价格
from agent.tools.crypto_data import crypto_tool

btc = crypto_tool.get_price('BTCUSDT')
print(f"BTC: ${btc['price']} ({btc['change_24h']}%)")

# 2. 获取 K 线
klines = crypto_tool.get_klines('ETHUSDT', '1d', 30)
for k in klines['klines']:
    print(f"Close: ${k['close']}")
```

### 方式 2: 使用分析工具

```python
from agent.tools.crypto_analysis import analysis_tool
from agent.tools.crypto_data import crypto_tool

# 获取 K 线并分析
klines = crypto_tool.get_klines('BTCUSDT', '1d', 100)
analysis = analysis_tool.analyze_trend(klines['klines'])

print(analysis['summary'])
# 输出示例：当前趋势：多头 (MA7>MA30)。RSI: 53.57 (中性)。
```

### 方式 3: 通过 Agent 对话（推荐）

当 dogeAgent 启动后，用户可以直接询问：

```
用户：BTC 现在什么价格？
Doge: BTCUSDT: $69648.29 (-0.965% 24h) | 高：$71777.0 | 低：$69266.06

用户：分析下 ETH 走势
Doge: 📊 ETHUSDT 分析 (1d)
     当前价：$2012.83
     趋势：多头 (MA7>MA30)
     RSI: 53.57 (中性)
     MA7: $2050 | MA30: $1980
     总结：当前趋势：多头。RSI 中性，未超买也未超卖。

用户：BTC 技术分析
Doge: 调用 analyze_crypto 工具返回详细分析
```

---

## 🛠️ 工具说明

### 1. `get_crypto_price(symbol)`

获取加密货币实时价格和 24 小时统计

**参数**:
- `symbol`: 币种符号，如 `'BTCUSDT'`, `'ETHUSDT'`, `'SOLUSDT'`

**返回示例**:
```
BTCUSDT: $69648.29 (-0.965% 24h) | 高：$71777.0 | 低：$69266.06 | 成交量：$28,456,789,012
```

### 2. `analyze_crypto(symbol, interval)`

分析加密货币趋势和技术指标

**参数**:
- `symbol`: 币种符号，默认 `'BTCUSDT'`
- `interval`: K 线间隔，如 `'1d'` (日 K), `'1h'` (小时 K), `'4h'` (4 小时 K)

**返回示例**:
```
📊 BTCUSDT 分析 (1d)
当前价：$69648.29
趋势：多头 (MA7>MA30)
RSI: 53.57 (中性)
MA7: $68609.7 | MA30: $67870.58
总结：当前趋势：多头 (MA7>MA30)。RSI: 53.57 (中性)。MA7: 68609.7 | MA30: 67870.58。
```

---

## 📊 技术指标说明

### RSI (相对强弱指数)
| RSI 范围 | 解读 | 含义 |
|---------|------|------|
| > 70 | 超买 | 可能回调 |
| 55-70 | 偏强 | 多头占优 |
| 45-55 | 中性 | 震荡整理 |
| 30-45 | 偏弱 | 空头占优 |
| < 30 | 超卖 | 可能反弹 |

### MA 均线趋势
- **多头**: MA7 > MA30 且价格 > MA7（上涨趋势）
- **空头**: MA7 < MA30 且价格 < MA7（下跌趋势）
- **震荡**: 其他情况（横盘整理）

---

## 🔧 支持的交易对

所有 Binance USDT 交易对，常见币种：
- `BTCUSDT` - 比特币
- `ETHUSDT` - 以太坊
- `BNBUSDT` - 币安币
- `SOLUSDT` - Solana
- `XRPUSDT` - Ripple
- `DOGEUSDT` - 狗狗币
- `ADAUSDT` - Cardano
- 等等...

---

## 🧪 测试

运行测试脚本验证功能：

```bash
cd H:\openclawWk\workspace-magic\workspace\2026\03\10\dogeAgent
python test_crypto_tools.py
```

**测试输出示例**:
```
==================================================
测试加密货币工具
==================================================
[1] 测试 BTC 价格查询...
[OK] BTC: $69648.29 (-0.965% 24h)
     高：$71777.0 | 低：$69266.06

[2] 测试 ETH 价格查询...
[OK] ETH: $2012.83 (-1.779% 24h)

[3] 测试 K 线数据获取...
[OK] 获取 30 条 K 线
     最新收盘价：$69648.29

[4] 测试趋势分析...
[OK] 分析成功:
     趋势：多头 (MA7>MA30)
     RSI: 53.57
     总结：当前趋势：多头 (MA7>MA30)。RSI: 53.57 (中性)。

[5] 测试工具注册...
[OK] 已注册 6 个工具:
     - get_current_time
     - get_current_date
     - calculate
     - get_crypto_price
     - analyze_crypto
     - get_weather
==================================================
测试完成
==================================================
```

---

## 📝 文件清单

| 文件 | 说明 |
|------|------|
| `agent/tools/crypto_data.py` | 数据获取工具（Binance/CoinGecko） |
| `agent/tools/crypto_analysis.py` | 技术分析工具（RSI/MA/趋势） |
| `tools/tool_registry.py` | 工具注册表 |
| `test_crypto_tools.py` | 测试脚本 |
| `CRYPTO_FEATURE.md` | 本文档 |

---

## ⚠️ 注意事项

1. **网络要求**: 需要能访问 Binance API（可能需要代理）
2. **API 限制**: Binance 有速率限制，避免频繁调用
3. **投资建议**: 本工具仅供参考，不构成投资建议
4. **数据延迟**: 实时数据可能有轻微延迟

---

## 🔜 后续扩展

### 短期 (v1.1)
- [ ] 添加更多技术指标（MACD、布林带）
- [ ] 价格预警功能（Telegram 通知）
- [ ] 支持更多交易所（OKX、Coinbase）

### 中期 (v1.2)
- [ ] 链上数据监控（鲸鱼动向）
- [ ] 社交媒体情绪分析
- [ ] 自定义指标参数

### 长期 (v2.0)
- [ ] 量化交易策略回测
- [ ] 自动交易执行
- [ ] 投资组合管理

---

**维护者**: SuperAgent  
**更新日期**: 2026-03-11  
**状态**: ✅ 生产就绪
