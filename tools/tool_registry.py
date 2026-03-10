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
- get_weather: 查询指定城市的实时天气。参数：location (城市名，如"北京"、"上海"、"赣州")
"""

@tool
def get_weather(location: str) -> str:
    """
    查询指定城市的实时天气
    
    这个工具会查询指定城市的当前天气，包括温度、天气状况和湿度。
    
    Args:
        location: 城市名称，必须是具体的城市名，如 "北京"、"上海"、"广州"、"赣州"、"龙岩"
    
    Returns:
        格式化的天气信息字符串
    """
    try:
        # 验证参数
        if not location or not isinstance(location, str) or not location.strip():
            logger.error(f"Invalid location parameter: {location}")
            return "汪...请提供正确的城市名呢！🐕"
        
        location = location.strip()
        logger.info(f"Calling weather tool for location: {location}")
        
        from tools.weather_tool import get_weather_sync
        result = get_weather_sync(location)
        
        logger.info(f"Weather tool result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"天气查询失败：{e}", exc_info=True)
        return f"汪...天气查询出错了：{str(e)}"

# 工具列表
ALL_TOOLS = [get_weather]

def get_all_tools():
    """获取所有可用工具"""
    return ALL_TOOLS

def get_tools_description():
    """获取工具描述"""
    return TOOLS_DESCRIPTION
