"""
插件基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class Plugin(ABC):
    """插件基类"""
    
    def __init__(self, plugin_id: str, name: str, version: str):
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.enabled = True
        self.config = {}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """关闭插件"""
        pass
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict) -> Optional[str]:
        """处理消息"""
        pass
    
    def get_commands(self) -> List[Dict[str, str]]:
        """获取命令列表"""
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取插件元数据"""
        return {
            "id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled
        }

class CommandPlugin(Plugin):
    """命令插件"""
    
    def __init__(self, plugin_id: str, name: str, version: str, command_prefix: str = "!"):
        super().__init__(plugin_id, name, version)
        self.command_prefix = command_prefix
        self.commands = {}
    
    def register_command(self, command: str, handler, description: str = ""):
        """注册命令"""
        self.commands[command] = {
            "handler": handler,
            "description": description
        }
    
    async def process_message(self, message: str, context: Dict) -> Optional[str]:
        """处理命令消息"""
        if not message.startswith(self.command_prefix):
            return None
        
        parts = message[1:].split()
        if not parts:
            return None
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in self.commands:
            handler = self.commands[cmd]["handler"]
            return await handler(args, context)
        
        return None
    
    def get_commands(self) -> List[Dict[str, str]]:
        """获取命令列表"""
        return [
            {
                "command": f"{self.command_prefix}{cmd}",
                "description": info["description"]
            }
            for cmd, info in self.commands.items()
        ]
