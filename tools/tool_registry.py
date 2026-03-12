"""
Tool Registry - 管理所有工具
使用延迟加载避免循环导入
"""
import logging
import sys
from pathlib import Path
from typing import List, Callable, Any

logger = logging.getLogger("dogeAgent.tools.registry")

# 工具列表
_tools: List = []
_tools_initialized = False

def _load_crypto_tools():
    """延迟加载加密货币工具"""
    try:
        from agent.tools.crypto_data import crypto_tool
        from agent.tools.crypto_analysis import analysis_tool
        from langchain_core.tools import tool
        
        @tool
        def get_crypto_price(symbol: str) -> str:
            """
            获取加密货币实时价格
            :param symbol: 币种符号，如 'BTCUSDT', 'ETHUSDT', 'DOGEUSDT'
            """
            result = crypto_tool.get_price(symbol)
            if result['success']:
                return f"{result['symbol']}: ${result['price']} ({result['change_24h']}% 24h) | 高：${result['high_24h']} | 低：${result['low_24h']} | 成交量：${result['quote_volume']:,.0f}"
            else:
                return f"获取价格失败：{result['error']}"
        
        @tool
        def analyze_crypto(symbol: str = 'BTCUSDT', interval: str = '1d') -> str:
            """
            分析加密货币趋势
            :param symbol: 币种符号，如 'BTCUSDT'
            :param interval: K 线间隔，如 '1d' (日 K), '1h' (小时 K)
            """
            klines_result = crypto_tool.get_klines(symbol, interval, 100)
            if not klines_result['success']:
                return f"获取 K 线失败：{klines_result['error']}"
            
            analysis = analysis_tool.analyze_trend(klines_result['klines'])
            if analysis['success']:
                rsi_text = f"{analysis['rsi']} ({analysis_tool.interpret_rsi(analysis['rsi'])})" if analysis['rsi'] else "N/A"
                return (
                    f"📊 {symbol} 分析 ({interval})\n"
                    f"当前价：${analysis['current_price']}\n"
                    f"趋势：{analysis['trend']}\n"
                    f"RSI: {rsi_text}\n"
                    f"MA7: ${analysis['ma_7']} | MA30: ${analysis['ma_30']}\n"
                    f"总结：{analysis['summary']}"
                )
            else:
                return f"分析失败：{analysis['error']}"
        
        return [get_crypto_price, analyze_crypto]
    except Exception as e:
        logger.warning(f"加密货币工具加载失败：{e}")
        return []

def _init_tools():
    """初始化工具列表（只执行一次）"""
    global _tools, _tools_initialized
    if _tools_initialized:
        return
    
    from langchain_core.tools import tool
    from datetime import datetime
    
    # 基础工具
    @tool
    def get_current_time() -> str:
        """获取当前时间"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @tool
    def get_current_date() -> str:
        """获取当前日期"""
        return datetime.now().strftime("%Y年%m月%d日 %A")
    
    @tool
    def calculate(expression: str) -> str:
        """
        计算数学表达式
        :param expression: 数学表达式，如 "2+2" 或 "10*5"
        """
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"计算错误：{e}"
    
    # 天气工具（占位符）
    @tool
    def get_weather(location: str) -> str:
        """
        获取指定城市的天气
        :param location: 城市名，如 '北京' 或 '上海'
        """
        return f"🌤️ {location} 天气数据暂缺"
    
    _tools = [get_current_time, get_current_date, calculate, get_weather]
    
    # 加载加密货币工具
    crypto_tools = _load_crypto_tools()
    _tools.extend(crypto_tools)
    
    _tools_initialized = True
    logger.info(f"工具初始化完成，共 {len(_tools)} 个工具")
    
    if crypto_tools:
        logger.info(f"  - 加密货币工具：{len(crypto_tools)} 个")

def get_all_tools() -> List:
    """获取所有已注册的工具"""
    _init_tools()
    return _tools

def register_tool(tool_func):
    """注册新工具"""
    _init_tools()
    _tools.append(tool_func)
    logger.info(f"工具已注册：{tool_func.name}")
    return tool_func

# 测试
if __name__ == "__main__":
    print("已注册工具:")
    tools = get_all_tools()
    for t in tools:
        print(f"  - {t.name}: {t.description[:60]}...")
