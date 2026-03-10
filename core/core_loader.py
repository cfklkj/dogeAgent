"""
核心文件加载器 - 读取和管理 Doge 的核心配置文件
"""
import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class CoreLoader:
    """核心文件加载器"""
    
    def __init__(self, core_dir: str = None):
        """
        初始化核心文件加载器
        
        Args:
            core_dir: 核心文件目录，默认为 agent/../core
        """
        if core_dir is None:
            # 默认使用项目根目录下的 core 文件夹
            current_dir = Path(__file__).parent
            self.core_dir = current_dir.parent / "core"
        else:
            self.core_dir = Path(core_dir)
        
        self.soul = {}
        self.identity = {}
        self.memory = {}
        self.collaboration = {}
        self.tools = {}
        
        logger.info(f"Core loader initialized with directory: {self.core_dir}")
    
    def load_all(self) -> bool:
        """加载所有核心文件"""
        try:
            self.load_soul()
            self.load_identity()
            self.load_memory()
            self.load_collaboration()
            self.load_tools()
            logger.info("All core files loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load core files: {e}")
            return False
    
    def load_soul(self) -> Dict:
        """加载 SOUL.md"""
        try:
            soul_path = self.core_dir / "SOUL.md"
            if soul_path.exists():
                with open(soul_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.soul = self._parse_soul(content)
                    logger.info(f"SOUL.md loaded: {len(self.soul)} sections")
            else:
                logger.warning(f"SOUL.md not found at {soul_path}")
        except Exception as e:
            logger.error(f"Failed to load SOUL.md: {e}")
        return self.soul
    
    def load_identity(self) -> Dict:
        """加载 IDENTITY.md"""
        try:
            identity_path = self.core_dir / "IDENTITY.md"
            if identity_path.exists():
                with open(identity_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.identity = self._parse_identity(content)
                    logger.info(f"IDENTITY.md loaded: {len(self.identity)} sections")
            else:
                logger.warning(f"IDENTITY.md not found at {identity_path}")
        except Exception as e:
            logger.error(f"Failed to load IDENTITY.md: {e}")
        return self.identity
    
    def load_memory(self) -> Dict:
        """加载 MEMORY.md"""
        try:
            memory_path = self.core_dir / "MEMORY.md"
            if memory_path.exists():
                with open(memory_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.memory = self._parse_memory(content)
                    logger.info(f"MEMORY.md loaded: {len(self.memory)} sections")
            else:
                logger.warning(f"MEMORY.md not found at {memory_path}")
        except Exception as e:
            logger.error(f"Failed to load MEMORY.md: {e}")
        return self.memory
    
    def load_collaboration(self) -> Dict:
        """加载 COLLABORATION.md"""
        try:
            collab_path = self.core_dir / "COLLABORATION.md"
            if collab_path.exists():
                with open(collab_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.collaboration = self._parse_collaboration(content)
                    logger.info(f"COLLABORATION.md loaded: {len(self.collaboration)} sections")
            else:
                logger.warning(f"COLLABORATION.md not found at {collab_path}")
        except Exception as e:
            logger.error(f"Failed to load COLLABORATION.md: {e}")
        return self.collaboration
    
    def load_tools(self) -> Dict:
        """加载 TOOLS.md"""
        try:
            tools_path = self.core_dir / "TOOLS.md"
            if tools_path.exists():
                with open(tools_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.tools = self._parse_tools(content)
                    logger.info(f"TOOLS.md loaded: {len(self.tools)} sections")
            else:
                logger.warning(f"TOOLS.md not found at {tools_path}")
        except Exception as e:
            logger.error(f"Failed to load TOOLS.md: {e}")
        return self.tools
    
    def _parse_soul(self, content: str) -> Dict:
        """解析 SOUL.md"""
        return {
            'raw_content': content,
            'core_identity': self._extract_section(content, '核心身份'),
            'values': self._extract_section(content, '核心价值观'),
            'principles': self._extract_section(content, '行为准则')
        }
    
    def _parse_identity(self, content: str) -> Dict:
        """解析 IDENTITY.md"""
        return {
            'raw_content': content,
            'basic_info': self._extract_section(content, '基本信息'),
            'personality': self._extract_section(content, '性格特征'),
            'communication_style': self._extract_section(content, '沟通风格')
        }
    
    def _parse_memory(self, content: str) -> Dict:
        """解析 MEMORY.md"""
        return {
            'raw_content': content,
            'user_info': self._extract_section(content, '关于用户'),
            'history': self._extract_section(content, '对话历史摘要'),
            'knowledge': self._extract_section(content, '学到的知识')
        }
    
    def _parse_collaboration(self, content: str) -> Dict:
        """解析 COLLABORATION.md"""
        return {
            'raw_content': content,
            'principles': self._extract_section(content, '工具使用原则'),
            'tools': self._extract_section(content, '可用工具清单'),
            'workflow': self._extract_section(content, '工具调用流程')
        }
    
    def _parse_tools(self, content: str) -> Dict:
        """解析 TOOLS.md"""
        return {
            'raw_content': content,
            'available_tools': self._extract_section(content, '已实现工具'),
            'planned_tools': self._extract_section(content, '规划中工具')
        }
    
    def _extract_section(self, content: str, section_title: str) -> str:
        """提取指定章节内容"""
        try:
            # 查找章节标题
            start_marker = f"## {section_title}"
            start_idx = content.find(start_marker)
            if start_idx == -1:
                return ""
            
            # 找到下一个二级标题
            start_idx += len(start_marker)
            next_section_idx = content.find("\n## ", start_idx)
            
            if next_section_idx == -1:
                # 没有下一个章节，取到文件末尾
                return content[start_idx:].strip()
            else:
                return content[start_idx:next_section_idx].strip()
        except Exception as e:
            logger.error(f"Failed to extract section '{section_title}': {e}")
            return ""
    
    def get_system_prompt(self) -> str:
        """
        根据核心文件生成系统提示词
        
        Returns:
            完整的系统提示词
        """
        # 优化的系统提示词 - 强调城市名准确性
        system_prompt = """你是一只可爱的柴犬宠物助手，名字叫 Doge。
你友好、活泼、聪明，喜欢帮助用户。
你的回答应该简洁、有趣，偶尔带点狗狗的可爱语气。

【重要能力】
你有查询天气的能力！当用户询问天气相关的问题时，你必须使用天气工具查询。

【关键规则】
1. 用户提到具体城市时（如"赣州天气"、"北京天气"），必须使用该城市名调用天气工具
2. 用户没有指定城市时，询问用户想查哪个城市
3. 工具调用时必须准确传递城市名，不能改变或替换

【天气查询示例】
用户："赣州天气" → 调用 get_weather("赣州")
用户："北京天气怎么样" → 调用 get_weather("北京")
用户："上海今天下雨吗" → 调用 get_weather("上海")
用户："天气怎么样" → 回复："汪！请告诉我你想查哪个城市的天气呀？"

【注意事项】
- 不要改变用户提到的城市名
- 如果工具返回结果，根据结果友好回复
- 如果工具调用失败，诚实告知用户

如果不知道答案，诚实地告诉用户。
"""
        
        return system_prompt

# 全局核心加载器实例
_core_loader: Optional[CoreLoader] = None

def get_core_loader() -> CoreLoader:
    """获取全局核心加载器实例"""
    global _core_loader
    if _core_loader is None:
        _core_loader = CoreLoader()
        _core_loader.load_all()
    return _core_loader
