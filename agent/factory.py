"""
Agent 工厂 - 创建和管理 LangChain Agent
支持工具调用和核心文件加载
"""
import logging
import re
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

# 使用模块日志器
logger = logging.getLogger("dogeAgent.agent.factory")

class AgentFactory:
    """Agent 工厂类"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or DEFAULT_MODEL_PROVIDER
        self.llm = None
        self.tools = get_all_tools()
        
        logger.info("初始化 AgentFactory...")
        
        # 加载核心文件
        try:
            from core.core_loader import get_core_loader
            core_loader = get_core_loader()
            self.system_prompt = core_loader.get_system_prompt()
            logger.info("核心文件加载成功")
        except Exception as e:
            logger.warning(f"核心文件加载失败：{e}，使用默认提示词")
            self.system_prompt = self._get_default_prompt()
        
        self._init_llm()
        logger.info(f"AgentFactory 初始化完成，provider={self.provider}")
    
    def _get_default_prompt(self) -> str:
        """获取默认系统提示词"""
        return """你是一只可爱的柴犬宠物助手，名字叫 Doge。
你友好、活泼、聪明，喜欢帮助用户。
你的回答应该简洁、有趣，偶尔带点狗狗的可爱语气。

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
    
    def _init_llm(self):
        """初始化 LLM"""
        try:
            logger.info(f"开始初始化 LLM，provider={self.provider}")
            
            if self.provider == "nvidia":
                if not NVIDIA_API_KEY:
                    logger.error("NVIDIA API Key 未配置")
                    raise ValueError("NVIDIA API Key 未配置")
                
                logger.info(f"使用 NVIDIA 模型：{MODEL_CONFIG['nvidia']['model']}")
                self.llm = ChatNVIDIA(
                    model=MODEL_CONFIG["nvidia"]["model"],
                    base_url=NVIDIA_BASE_URL,
                    api_key=NVIDIA_API_KEY,
                    temperature=0.7,
                    max_tokens=2048,
                )
                # 绑定工具
                if self.tools:
                    logger.info(f"绑定 {len(self.tools)} 个工具到 LLM")
                    self.llm = self.llm.bind_tools(self.tools)
                logger.info("NVIDIA LLM 初始化成功")
                
            elif self.provider == "google":
                if not GOOGLE_API_KEY:
                    logger.error("Google API Key 未配置")
                    raise ValueError("Google API Key 未配置")
                
                logger.info(f"使用 Google 模型：{MODEL_CONFIG['google']['model']}")
                self.llm = ChatGoogleGenerativeAI(
                    model=MODEL_CONFIG["google"]["model"],
                    google_api_key=GOOGLE_API_KEY,
                    temperature=0.7,
                    max_output_tokens=2048,
                )
                logger.info("Google LLM 初始化成功")
            else:
                raise ValueError(f"不支持的模型提供商：{self.provider}")
                
        except Exception as e:
            logger.error(f"LLM 初始化失败：{e}", exc_info=True)
            raise
    
    def switch_provider(self, provider: str) -> bool:
        """切换模型提供商"""
        if provider not in MODEL_CONFIG:
            logger.error(f"不支持的模型提供商：{provider}")
            return False
        
        self.provider = provider
        self._init_llm()
        return True
    
    def _extract_city(self, message: str) -> str:
        """从消息中提取城市名"""
        # 常见城市列表
        cities = [
            '北京', '上海', '广州', '深圳', '成都', '杭州', '武汉', '西安',
            '南京', '重庆', '天津', '苏州', '厦门', '青岛', '大连', '长沙',
            '郑州', '沈阳', '哈尔滨', '福州', '南昌', '贵阳', '昆明', '南宁',
            '海口', '三亚', '拉萨', '西宁', '银川', '乌鲁木齐', '呼和浩特',
            '太原', '石家庄', '济南', '合肥', '长春', '龙岩', '赣州'
        ]
        
        # 尝试从消息中匹配城市
        for city in cities:
            if city in message:
                logger.debug(f"从城市列表中找到城市：{city}")
                return city
        
        # 尝试用正则匹配"XX 的天气"格式
        match = re.search(r'([一亩六〇 - 龠 A-Za-z]+) 的天气', message)
        if match:
            potential_city = match.group(1)
            if potential_city and potential_city != '':
                logger.debug(f"从正则匹配到城市：{potential_city}")
                return potential_city
        
        logger.debug("未找到城市")
        return ""
    
    def chat(self, message: str, history: List[Tuple[str, str]] = None) -> str:
        """
        与 Agent 对话（支持工具调用）
        """
        try:
            logger.info(f"收到消息：{message[:100]}...")
            logger.debug(f"完整消息：{message}")
            logger.debug(f"历史消息：{history}")
            
            # 构建消息历史
            messages = [SystemMessage(content=self.system_prompt)]
            logger.debug(f"系统提示词长度：{len(self.system_prompt)}")
            
            # 安全地处理历史记录
            if history:
                for item in history:
                    if not isinstance(item, (list, tuple)) or len(item) != 2:
                        logger.warning(f"无效的历史记录：{item}")
                        continue
                    
                    role, content = item
                    if not isinstance(content, str) or not content:
                        logger.warning(f"无效的内容：{content}")
                        continue
                    
                    if role == "human":
                        messages.append(HumanMessage(content=content))
                    elif role == "ai":
                        messages.append(AIMessage(content=content))
            
            # 添加当前消息
            if message and isinstance(message, str):
                messages.append(HumanMessage(content=message))
                logger.debug(f"添加用户消息：{message[:50]}...")
            else:
                messages.append(HumanMessage(content=str(message) if message else ""))
            
            logger.info(f"发送 {len(messages)} 条消息到 LLM，绑定 {len(self.tools)} 个工具")
            
            # 调用 LLM
            logger.debug("开始调用 LLM...")
            response = self.llm.invoke(messages)
            logger.debug(f"LLM 响应类型：{type(response)}")
            logger.debug(f"LLM 响应内容：{str(response.content)[:200]}...")
            
            # 检查是否有工具调用
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"检测到工具调用：{len(response.tool_calls)} 个")
                
                # 执行工具调用
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get('name')
                    tool_args = tool_call.get('args', {})
                    
                    logger.info(f"执行工具：{tool_name}, 参数：{tool_args}")
                    
                    if tool_name == 'get_weather':
                        location = tool_args.get('location', '')
                        
                        if not location:
                            location = self._extract_city(message)
                            logger.info(f"从消息中提取城市：{location}")
                        
                        if location:
                            from tools.weather_tool import get_weather_sync
                            logger.info(f"调用天气工具查询：{location}")
                            tool_result = get_weather_sync(location)
                            logger.info(f"天气工具返回结果：{tool_result}")
                            
                            # 将工具结果添加到对话中
                            messages.append(AIMessage(content=f"正在查询{location}的天气..."))
                            messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call.get('id', '')))
                            
                            # 再次调用 LLM 获取最终回复
                            logger.info("再次调用 LLM 获取最终回复...")
                            final_response = self.llm.invoke(messages)
                            logger.debug(f"最终回复内容：{str(final_response.content)[:200]}...")
                            return final_response.content
                        else:
                            return '汪！请告诉我你想查哪个城市的天气呀？比如"北京天气"或"上海天气"~ 🐕'
            
            # 没有工具调用，直接返回
            result = response.content
            logger.info(f"返回结果：{result[:100]}...")
            return result
            
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
        logger.info("创建新的 Agent 实例...")
        _agent_instance = AgentFactory(provider)
    return _agent_instance

def reset_agent():
    """重置 Agent 实例"""
    global _agent_instance
    logger.info("重置 Agent 实例...")
    _agent_instance = None
