"""
插件管理器
"""
import importlib
import inspect
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from .plugin_base import Plugin

logger = logging.getLogger(__name__)

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: Path = None):
        self.plugin_dir = plugin_dir or Path(__file__).parent / "installed"
        self.plugin_dir.mkdir(exist_ok=True)
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_instances: Dict[str, Plugin] = {}
        self.disabled_plugins: set = set()
        
        logger.info(f"插件管理器初始化，插件目录: {self.plugin_dir}")
    
    def discover_plugins(self):
        """发现可用插件"""
        for plugin_path in self.plugin_dir.glob("*.py"):
            if plugin_path.name.startswith("_"):
                continue
            
            module_name = plugin_path.stem
            try:
                spec = importlib.util.spec_from_file_location(
                    f"plugins.installed.{module_name}",
                    plugin_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, Plugin) and obj != Plugin:
                        plugin_id = f"{module_name}.{name}"
                        self.plugins[plugin_id] = obj
                        logger.info(f"发现插件: {plugin_id}")
            except Exception as e:
                logger.error(f"加载插件失败 {plugin_path}: {e}")
    
    async def load_plugin(self, plugin_id: str, **kwargs) -> Optional[Plugin]:
        """加载插件"""
        if plugin_id not in self.plugins:
            logger.error(f"插件不存在: {plugin_id}")
            return None
        
        if plugin_id in self.disabled_plugins:
            logger.info(f"插件已禁用: {plugin_id}")
            return None
        
        try:
            plugin_class = self.plugins[plugin_id]
            plugin = plugin_class(**kwargs)
            
            if await plugin.initialize():
                self.plugin_instances[plugin_id] = plugin
                logger.info(f"插件加载成功: {plugin.name} v{plugin.version}")
                return plugin
            else:
                logger.error(f"插件初始化失败: {plugin_id}")
        except Exception as e:
            logger.error(f"加载插件异常 {plugin_id}: {e}")
        
        return None
    
    async def load_all_plugins(self):
        """加载所有插件"""
        tasks = []
        for plugin_id in self.plugins:
            if plugin_id not in self.disabled_plugins:
                tasks.append(self.load_plugin(plugin_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        loaded = [r for r in results if isinstance(r, Plugin)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        logger.info(f"插件加载完成: {len(loaded)}成功, {len(failed)}失败")
    
    async def process_message(self, message: str, context: Dict) -> Optional[str]:
        """处理消息"""
        for plugin in self.plugin_instances.values():
            if plugin.enabled:
                try:
                    response = await plugin.process_message(message, context)
                    if response:
                        return response
                except Exception as e:
                    logger.error(f"插件处理失败 {plugin.name}: {e}")
        
        return None
    
    def get_all_plugins_info(self) -> List[Dict]:
        """获取所有插件信息"""
        info = []
        
        for plugin_id, plugin in self.plugin_instances.items():
            info.append({
                **plugin.get_metadata(),
                "status": "loaded",
                "commands": plugin.get_commands()
            })
        
        for plugin_id, plugin_class in self.plugins.items():
            if plugin_id not in self.plugin_instances:
                info.append({
                    "id": plugin_id,
                    "name": plugin_class.__name__,
                    "status": "disabled" if plugin_id in self.disabled_plugins else "unloaded",
                    "version": "unknown"
                })
        
        return info

# 全局插件管理器
plugin_manager = PluginManager()
