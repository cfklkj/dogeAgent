"""
和风天气API集成
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class HeFengWeather:
    """和风天气API客户端"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://devapi.qweather.com/v7"
        self.geo_url = "https://geoapi.qweather.com/v2"
        logger.info("和风天气客户端初始化")
    
    async def get_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """获取天气信息"""
        if not self.api_key:
            return self._simulate_weather(location)
        
        try:
            # 获取城市ID
            location_id = await self._get_location_id(location)
            if not location_id:
                return None
            
            # 获取实时天气
            current = await self._get_current_weather(location_id)
            
            return {
                "location": location,
                "update_time": datetime.now().isoformat(),
                "current": current,
                "source": "和风天气"
            }
        except Exception as e:
            logger.error(f"获取天气失败: {e}")
            return self._simulate_weather(location)
    
    async def _get_location_id(self, location: str) -> Optional[str]:
        """获取城市ID"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {"key": self.api_key, "location": location}
                async with session.get(
                    f"{self.geo_url}/city/lookup",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == "200":
                            return data["location"][0]["id"]
        except Exception as e:
            logger.error(f"获取城市ID失败: {e}")
        return None
    
    async def _get_current_weather(self, location_id: str) -> Dict[str, Any]:
        """获取实时天气"""
        async with aiohttp.ClientSession() as session:
            params = {"key": self.api_key, "location": location_id}
            async with session.get(
                f"{self.base_url}/weather/now",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == "200":
                        now = data.get("now", {})
                        return {
                            "temp": now.get("temp"),
                            "feels_like": now.get("feelsLike"),
                            "humidity": now.get("humidity"),
                            "condition": now.get("text"),
                            "wind_dir": now.get("windDir"),
                            "wind_speed": now.get("windSpeed")
                        }
        return {}
    
    def _simulate_weather(self, location: str) -> Dict[str, Any]:
        """模拟天气数据"""
        import random
        temps = ["15°C", "18°C", "20°C", "22°C", "25°C"]
        conditions = ["晴", "多云", "阴", "小雨"]
        
        return {
            "location": location,
            "update_time": datetime.now().isoformat(),
            "current": {
                "temp": random.choice(temps),
                "condition": random.choice(conditions),
                "humidity": f"{random.randint(40, 80)}%"
            },
            "source": "模拟数据"
        }

class WeatherManager:
    """天气管理器"""
    
    def __init__(self, api_key: str = ""):
        self.client = HeFengWeather(api_key)
    
    async def get_weather(self, location: str = "北京") -> str:
        """获取天气并格式化返回"""
        data = await self.client.get_weather(location)
        
        if not data:
            return f"汪...查不到{location}的天气呢 🐶"
        
        current = data.get("current", {})
        temp = current.get("temp", "?")
        condition = current.get("condition", "未知")
        humidity = current.get("humidity", "?")
        
        return f"""汪！{location}的天气来啦~

🌡️ 当前温度：{temp}
☁️ 天气状况：{condition}
💧 湿度：{humidity}

汪！要照顾好自己哦 🐾"""
