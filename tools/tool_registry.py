"""
工具注册表 - 管理所有可用工具
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

logger = logging.getLogger(__name__)

# 工具描述
TOOLS_DESCRIPTION = """
可用工具：
- weather: 查询指定城市的实时天气
"""

@tool
def get_weather(location: str) -> str:
    """
    查询指定城市的实时天气
    
    Args:
        location: 城市名称，如 "北京"、"上海"
    
    Returns:
        格式化的天气信息
    """
    try:
        from tools.weather_tool import get_weather_sync
        return get_weather_sync(location)
    except Exception as e:
        logger.error(f"天气查询失败：{e}")
        return f"天气查询失败：{str(e)}"

# 工具列表
ALL_TOOLS = [get_weather]

def get_all_tools():
    """获取所有可用工具"""
    return ALL_TOOLS

def get_tools_description():
    """获取工具描述"""
    return TOOLS_DESCRIPTION
