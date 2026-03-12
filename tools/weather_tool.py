"""
Weather Tool - 天气查询工具
使用和风天气 API 或模拟数据
"""
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("dogeAgent.tools.weather")

# 和风天气 API 配置 (需要用户在 .env 中配置)
HEFENG_API_KEY = ""  # 从 .env 读取
HEFENG_BASE_URL = "https://devapi.qweather.com/v7"

def get_weather_sync(location: str) -> str:
    """
    同步获取天气 (用于工具调用)
    :param location: 城市名
    :return: 天气描述字符串
    """
    # 注意：这是简化版本，实际使用需要实现城市代码查询和 API 调用
    return f"🌤️ {location} 天气数据暂缺，请配置和风天气 API Key"

# 如果需要使用真实 API，请配置 HEFENG_API_KEY 并实现完整逻辑
