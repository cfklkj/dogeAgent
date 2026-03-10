"""
天气查询工具 - 简单的同步版本
"""
import logging
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

def get_weather_sync(location: str = "北京", api_key: str = "") -> str:
    """
    同步获取天气（用于 LangChain 工具）
    
    Args:
        location: 城市名
        api_key: 和风天气 API Key
    
    Returns:
        格式化的天气信息
    """
    try:
        from weather.hefeng_weather import HeFengWeather
        
        client = HeFengWeather(api_key)
        
        # 运行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            data = loop.run_until_complete(client.get_weather(location))
        finally:
            loop.close()
        
        if not data:
            return f"汪...查不到 {location} 的天气呢 🐶"
        
        current = data.get("current", {})
        temp = current.get("temp", "?")
        condition = current.get("condition", "未知")
        humidity = current.get("humidity", "?")
        
        return f"汪！{location}的天气：🌡️ {temp} | ☁️ {condition} | 💧 湿度{humidity}"
        
    except Exception as e:
        logger.error(f"天气查询失败：{e}")
        # 返回模拟数据
        import random
        temps = ["15°C", "18°C", "20°C", "22°C", "25°C"]
        conditions = ["晴", "多云", "阴", "小雨"]
        return f"汪！{location}的天气（模拟）：🌡️ {random.choice(temps)} | ☁️ {random.choice(conditions)}"
