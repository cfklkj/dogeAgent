"""
工具注册表
"""
from typing import Dict, Callable, Any, List

class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, func: Callable, description: str):
        """注册工具"""
        self._tools[name] = {
            "func": func,
            "description": description,
            "name": name
        }
    
    def get(self, name: str) -> Callable:
        """获取工具函数"""
        if name in self._tools:
            return self._tools[name]["func"]
        raise KeyError(f"工具不存在：{name}")
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有工具"""
        return list(self._tools.values())
    
    def get_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self._tools.keys())

# 全局工具注册表
registry = ToolRegistry()
