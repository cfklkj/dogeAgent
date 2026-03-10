"""
Agent 状态管理 - 管理 Agent 的生命周期状态
"""
import logging
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger("dogeAgent.agent.status")

class AgentStatus(Enum):
    """Agent 状态枚举"""
    INITIALIZING = "initializing"  # 初始化中
    READY = "ready"  # 就绪
    BUSY = "busy"  # 忙碌中
    ERROR = "error"  # 错误
    DISCONNECTED = "disconnected"  # 断开连接

class AgentStateManager:
    """
    Agent 状态管理器
    单例模式，全局共享状态
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if AgentStateManager._initialized:
            return
        
        self.status = AgentStatus.INITIALIZING
        self.error_message: Optional[str] = None
        self.last_update = datetime.now()
        self.message_count = 0
        self.error_count = 0
        self.provider: Optional[str] = None
        self.model: Optional[str] = None
        
        AgentStateManager._initialized = True
        logger.info("AgentStateManager initialized")
    
    def set_initializing(self):
        """设置为初始化中"""
        self.status = AgentStatus.INITIALIZING
        self.last_update = datetime.now()
        logger.info("Status: INITIALIZING")
    
    def set_ready(self, provider: str = None, model: str = None):
        """设置为就绪状态"""
        self.status = AgentStatus.READY
        self.last_update = datetime.now()
        if provider:
            self.provider = provider
        if model:
            self.model = model
        logger.info(f"Status: READY (provider={provider}, model={model})")
    
    def set_busy(self):
        """设置为忙碌中"""
        if self.status == AgentStatus.READY:
            self.status = AgentStatus.BUSY
            self.last_update = datetime.now()
            logger.info("Status: BUSY")
    
    def set_error(self, error_message: str):
        """设置为错误状态"""
        self.status = AgentStatus.ERROR
        self.error_message = error_message
        self.error_count += 1
        self.last_update = datetime.now()
        logger.error(f"Status: ERROR - {error_message}")
    
    def set_disconnected(self):
        """设置为断开连接"""
        self.status = AgentStatus.DISCONNECTED
        self.last_update = datetime.now()
        logger.info("Status: DISCONNECTED")
    
    def increment_message_count(self):
        """增加消息计数"""
        self.message_count += 1
    
    def get_status_dict(self) -> Dict[str, Any]:
        """
        获取状态字典
        
        Returns:
            包含所有状态信息的字典
        """
        return {
            "status": self.status.value,
            "provider": self.provider,
            "model": self.model,
            "error_message": self.error_message,
            "message_count": self.message_count,
            "error_count": self.error_count,
            "last_update": self.last_update.isoformat()
        }
    
    def is_ready(self) -> bool:
        """检查是否就绪"""
        return self.status == AgentStatus.READY
    
    def is_error(self) -> bool:
        """检查是否错误"""
        return self.status == AgentStatus.ERROR
    
    def is_busy(self) -> bool:
        """检查是否忙碌"""
        return self.status == AgentStatus.BUSY
    
    def reset(self):
        """重置状态"""
        self.status = AgentStatus.INITIALIZING
        self.error_message = None
        self.last_update = datetime.now()
        self.provider = None
        self.model = None
        logger.info("Status reset")

# 全局状态管理器实例
_state_manager: Optional[AgentStateManager] = None

def get_state_manager() -> AgentStateManager:
    """获取全局状态管理器实例"""
    global _state_manager
    if _state_manager is None:
        _state_manager = AgentStateManager()
    return _state_manager

def reset_state_manager():
    """重置状态管理器"""
    global _state_manager
    _state_manager = None
