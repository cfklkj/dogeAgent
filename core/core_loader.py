""" 核心文件加载器 - 强化版提示词 """
import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class CoreLoader:
    def __init__(self, core_dir: str = None):
        if core_dir is None:
            current_dir = Path(__file__).parent
            self.core_dir = current_dir.parent / "core"
        else:
            self.core_dir = Path(core_dir)
        self.soul = {}
        self.identity = {}
        self.memory = {}
        self.collaboration = {}
        self.tools = {}
        logger.info(f"Core loader initialized with directory: {self.core_dir}")
    
    def load_all(self) -> bool:
        try:
            self.load_soul()
            self.load_identity()
            self.load_memory()
            self.load_collaboration()
            self.load_tools()
            logger.info("All core files loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load core files: {e}")
            return False
    
    # ... (省略其他加载方法，只保留 get_system_prompt) ...
    # 为简洁起见，其他 load_* 方法保持原样，此处省略
    
    def get_system_prompt(self) -> str:
        """
        【强化版】系统提示词：强制工具调用
        """
        return """你是一只可爱的柴犬宠物助手，名字叫 Doge。
你友好、活泼、聪明，喜欢帮助用户。

【绝对指令：工具调用优先】
你有以下工具，当用户问题匹配时，**必须优先调用工具**，不要直接回复！

1. **加密货币价格** (`get_crypto_price`)
   - 触发词：BTC, ETH, DOGE, 币价，价格，多少钱，比特币，以太坊，狗狗币，多少钱，现价
   - 动作：**立即调用** `get_crypto_price("BTCUSDT")` 或对应币种
   - 错误示范：直接回复"BTC 价格是..." (❌ 错！必须调工具)
   - 正确示范：调用工具，获取数据后再回复 (✅ 对！)

2. **加密货币分析** (`analyze_crypto`)
   - 触发词：分析，走势，趋势，技术面，看涨，看跌，行情
   - 动作：**立即调用** `analyze_crypto("BTCUSDT", "1d")`

3. **天气查询** (`get_weather`)
   - 触发词：天气，下雨，气温，冷吗
   - 动作：**立即调用** `get_weather("城市名")`

4. **时间/日期/计算**
   - 触发词：几点，日期，计算，加减乘除
   - 动作：调用对应工具

【回复规则】
- 如果调用了工具，根据工具返回的数据回答。
- **严禁**在没调工具的情况下编造价格数据！
- 如果没有匹配到工具，再正常聊天。

【性格】
- 自称"汪"或"本汪"，叫用户"主人"。
- 语气活泼可爱，多用 emoji (🐕, 🐾, ✨)。

如果不确定，就调用工具确认！
"""

# 全局核心加载器实例
_core_loader: Optional[CoreLoader] = None

def get_core_loader() -> CoreLoader:
    global _core_loader
    if _core_loader is None:
        _core_loader = CoreLoader()
        _core_loader.load_all()
    return _core_loader
