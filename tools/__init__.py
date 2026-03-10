"""
工具模块 - 提供各种实用工具
"""
import logging
from datetime import datetime
from typing import List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%H:%M:%S")

@tool
def get_current_date() -> str:
    """获取当前日期"""
    return datetime.now().strftime("%Y年%m月%d日 %A")

@tool
def calculate(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2 + 2" 或 "10 * 5"
    
    Returns:
        计算结果
    """
    try:
        # 安全计算
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"

@tool
def get_weather(city: str = "北京") -> str:
    """
    获取天气信息（模拟版）
    
    Args:
        city: 城市名
    
    Returns:
        天气信息
    """
    # 模拟天气数据
    import random
    temps = ["15°C", "18°C", "20°C", "22°C", "25°C"]
    conditions = ["晴", "多云", "阴", "小雨", "大雨"]
    
    temp = random.choice(temps)
    condition = random.choice(conditions)
    
    return f"汪！{city}今天天气不错哦~ {condition}，气温{temp} 🐶"

def get_all_tools() -> List:
    """获取所有工具"""
    return [get_current_time, get_current_date, calculate, get_weather]

__all__ = ['get_current_time', 'get_current_date', 'calculate', 'get_weather', 'get_all_tools']
