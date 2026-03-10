"""
搜索引擎集成模块
"""
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DuckDuckGoSearch:
    """DuckDuckGo搜索（无需API key）"""
    
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """执行搜索"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {"q": query, "kl": "cn-chinese"}
                async with session.post(
                    self.base_url,
                    data=params,
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_results(html, num_results)
                    else:
                        logger.error(f"搜索请求失败: {response.status}")
        except Exception as e:
            logger.error(f"搜索异常: {e}")
        return []
    
    def _parse_results(self, html: str, num_results: int) -> List[Dict[str, str]]:
        """解析搜索结果"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='result')[:num_results]:
            try:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "snippet": snippet_elem.get_text(strip=True),
                        "url": result.find('a', class_='result__url').get('href', '')
                    })
            except Exception as e:
                logger.error(f"解析结果失败: {e}")
                continue
        
        return results

class SearchManager:
    """搜索管理器"""
    
    def __init__(self, engine: str = "duckduckgo"):
        self.engine = DuckDuckGoSearch()
        logger.info(f"搜索管理器初始化，使用引擎: {engine}")
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """执行搜索"""
        logger.info(f"执行搜索: {query}")
        results = await self.engine.search(query, num_results)
        
        if results:
            logger.info(f"获取到 {len(results)} 条结果")
        else:
            logger.warning("搜索无结果")
        
        return results
    
    def format_results(self, results: List[Dict[str, str]], query: str) -> str:
        """格式化搜索结果"""
        if not results:
            return f"汪...关于'{query}'没找到相关信息呢 🐶"
        
        response = f"关于'{query}'，我找到这些信息：\n\n"
        
        for i, result in enumerate(results[:3], 1):
            title = result.get("title", "无标题")
            snippet = result.get("snippet", "无摘要")
            response += f"{i}. {title}\n   {snippet}\n\n"
        
        response += "想了解更多可以告诉我哦 🐾"
        return response
