"""
Agent 工厂 - 创建和管理 LangChain Agent
支持工具调用
"""
import logging
from typing import Optional, Dict, Any, List, Tuple
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from config.settings import (
    NVIDIA_API_KEY, 
    NVIDIA_BASE_URL, 
    GOOGLE_API_KEY,
    DEFAULT_MODEL_PROVIDER
)
from models.config import MODEL_CONFIG
from tools.tool_registry import get_all_tools

logger = logging.getLogger(__name__)

# 系统提示词 - 强调工具使用
SYSTEM_PROMPT = """你是一只可爱的柴犬宠物助手，名字叫 Doge。
你友好、活泼、聪明，喜欢帮助用户。
你的回答应该简洁、有趣，偶尔带点狗狗的可爱语气。

【重要能力】
你有查询天气的能力！当用户询问天气相关的问题时，你必须使用天气工具查询。

天气相关问题示例：
- "今天天气怎么样"
- "天气如何"
- "明天会下雨吗"
- "未来三天龙岩的天气怎样"
- "北京天气"
- "上海今天下雨吗"

当你识别到天气相关的问题时：
1. 立即调用天气工具查询
2. 根据查询结果给出友好回复
3. 如果用户没有指定城市，可以询问用户想查哪个城市

如果不知道答案，诚实地告诉用户。
"""

class AgentFactory:
    """Agent 工厂类"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or DEFAULT_MODEL_PROVIDER
        self.llm = None
        self.tools = get_all_tools()
        self.system_prompt = SYSTEM_PROMPT
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
                # 绑定工具
                if self.tools:
                    self.llm = self.llm.bind_tools(self.tools)
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
    
    def chat(self, message: str, history: List[Tuple[str, str]] = None) -> str:
        """
        与 Agent 对话（支持工具调用）
        
        Args:
            message: 用户消息
            history: 历史对话记录 [(role, content), ...]
        
        Returns:
            Agent 回复
        """
        try:
            # 构建消息历史
            messages = [SystemMessage(content=self.system_prompt)]
            
            # 安全地处理历史记录
            if history:
                for item in history:
                    # 确保是有效的元组
                    if not isinstance(item, (list, tuple)) or len(item) != 2:
                        logger.warning(f"Invalid history item: {item}")
                        continue
                    
                    role, content = item
                    if not isinstance(content, str) or not content:
                        logger.warning(f"Invalid content in history: {content}")
                        continue
                    
                    if role == "human":
                        messages.append(HumanMessage(content=content))
                    elif role == "ai":
                        messages.append(AIMessage(content=content))
            
            # 添加当前消息
            if message and isinstance(message, str):
                messages.append(HumanMessage(content=message))
            else:
                messages.append(HumanMessage(content=str(message) if message else ""))
            
            logger.debug(f"Sending {len(messages)} messages to LLM with {len(self.tools)} tools")
            
            # 调用 LLM（可能包含工具调用）
            response = self.llm.invoke(messages)
            
            # 检查是否有工具调用
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"Tool calls detected: {len(response.tool_calls)}")
                # 执行工具调用
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get('name')
                    tool_args = tool_call.get('args', {})
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    # 执行工具
                    if tool_name == 'get_weather':
                        location = tool_args.get('location', '')
                        if not location:
                            # 尝试从消息中提取位置
                            if '龙岩' in message:
                                location = '龙岩'
                            elif '北京' in message:
                                location = '北京'
                            # ... 可以添加更多城市识别
                            
                        if location:
                            from tools.weather_tool import get_weather_sync
                            tool_result = get_weather_sync(location)
                            logger.info(f"Weather tool result: {tool_result}")
                            
                            # 将工具结果添加到对话中
                            messages.append(AIMessage(content=f"正在查询{location}的天气..."))
                            messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call.get('id', '')))
                            
                            # 再次调用 LLM 获取最终回复
                            final_response = self.llm.invoke(messages)
                            return final_response.content
                        else:
                            # 使用单引号避免转义问题
                            return '汪！请告诉我你想查哪个城市的天气呀？比如"北京天气"或"上海天气"~ 🐕'
            
            # 没有工具调用，直接返回
            return response.content
            
        except Exception as e:
            logger.error(f"对话失败：{e}", exc_info=True)
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
