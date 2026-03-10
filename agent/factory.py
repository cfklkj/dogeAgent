"""
Agent 工厂 - 创建和管理 LangChain Agent
"""
import logging
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import (
    NVIDIA_API_KEY, NVIDIA_BASE_URL, GOOGLE_API_KEY,
    DEFAULT_MODEL_PROVIDER
)
from models.config import MODEL_CONFIG
from tools import get_all_tools

logger = logging.getLogger(__name__)

class AgentFactory:
    """Agent 工厂类"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or DEFAULT_MODEL_PROVIDER
        self.llm = None
        self.tools = get_all_tools()
        self.system_prompt = """你是一只可爱的柴犬宠物助手，名字叫 Doge。
你友好、活泼、聪明，喜欢帮助用户。
你的回答应该简洁、有趣，偶尔带点狗狗的可爱语气。
你会使用各种工具来帮助用户解决问题。
如果不知道答案，诚实地告诉用户。"""
        self._init_llm()
    
    def _init_llm(self):
        """初始化 LLM"""
        try:
            if self.provider == "nvidia":
                if not NVIDIA_API_KEY:
                    logger.error("NVIDIA API Key 未配置")
                    raise ValueError("NVIDIA API Key 未配置")
                
                self.llm = ChatNVIDIA(
                    model=MODEL_CONFIG["nvidia"]["model"],
                    base_url=NVIDIA_BASE_URL,
                    api_key=NVIDIA_API_KEY,
                    temperature=0.7,
                    max_tokens=2048,
                )
                logger.info(f"NVIDIA LLM 初始化成功：{MODEL_CONFIG['nvidia']['model']}")
                
            elif self.provider == "google":
                if not GOOGLE_API_KEY:
                    logger.error("Google API Key 未配置")
                    raise ValueError("Google API Key 未配置")
                
                self.llm = ChatGoogleGenerativeAI(
                    model=MODEL_CONFIG["google"]["model"],
                    google_api_key=GOOGLE_API_KEY,
                    temperature=0.7,
                    max_output_tokens=2048,
                )
                logger.info(f"Google LLM 初始化成功：{MODEL_CONFIG['google']['model']}")
                
            else:
                raise ValueError(f"不支持的模型提供商：{self.provider}")
                
        except Exception as e:
            logger.error(f"LLM 初始化失败：{e}")
            raise
    
    def switch_provider(self, provider: str) -> bool:
        """切换模型提供商"""
        if provider not in MODEL_CONFIG:
            logger.error(f"不支持的模型提供商：{provider}")
            return False
        
        self.provider = provider
        self._init_llm()
        return True
    
    def chat(self, message: str, history: list = None) -> str:
        """
        与 Agent 对话
        
        Args:
            message: 用户消息
            history: 历史对话记录 [(role, content), ...]
        
        Returns:
            Agent 回复
        """
        try:
            # 构建消息历史
            messages = [SystemMessage(content=self.system_prompt)]
            
            if history:
                for role, content in history:
                    if role == "human":
                        messages.append(HumanMessage(content=content))
                    elif role == "ai":
                        messages.append(AIMessage(content=content))
            
            # 添加当前消息
            messages.append(HumanMessage(content=message))
            
            # 调用 LLM
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"对话失败：{e}")
            return f"汪...出错了：{str(e)}"
    
    def get_tools_description(self) -> str:
        """获取工具描述"""
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])


# 全局 Agent 实例
_agent_instance: Optional[AgentFactory] = None

def get_agent(provider: str = None) -> AgentFactory:
    """获取全局 Agent 实例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentFactory(provider)
    return _agent_instance

def reset_agent():
    """重置 Agent 实例"""
    global _agent_instance
    _agent_instance = None
