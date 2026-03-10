"""
桥接服务 - Electron 与 Python 之间的通信
注意：所有输出使用 UTF-8 编码，避免 Windows GBK 问题
"""
import sys
import os
import json
import logging
import io
import codecs
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv

# 强制设置标准输出为 UTF-8
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / '.env')

# 现在可以正确导入项目模块
from agent.factory import get_agent, reset_agent
from storage.session_store import session_store

# 配置日志 - 使用 UTF-8 编码
class UTF8StreamHandler(logging.StreamHandler):
    """UTF-8 编码的日志处理器"""
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # 使用 UTF-8 编码，错误替换
            stream.write(msg + self.terminator)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            # 安静地处理错误，避免死循环
            pass

# 设置日志
logger = logging.getLogger("bridge")
logger.setLevel(logging.INFO)

# 清除现有处理器
logger.handlers.clear()

# 添加 UTF-8 处理器
handler = UTF8StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)

# 也设置根日志
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers.clear()
root_handler = UTF8StreamHandler()
root_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
root_logger.addHandler(root_handler)

class BridgeService:
    """桥接服务"""
    
    def __init__(self):
        self.agent = None
        self.user_id = "default"
        self._initialized = False
    
    def init_agent(self, provider: str = None) -> Dict[str, Any]:
        """初始化 Agent"""
        if self._initialized:
            return {"status": "success", "message": "Agent 已初始化"}
        
        try:
            logger.info(f"Starting to initialize Agent, provider: {provider or 'default'}")
            self.agent = get_agent(provider)
            self._initialized = True
            logger.info(f"Agent initialized successfully, provider: {provider}")
            return {"status": "success", "message": "Agent 初始化成功"}
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "message": f"Agent 初始化失败：{str(e)}"}
    
    def chat(self, message: str) -> Dict[str, Any]:
        """
        处理聊天消息
        
        Args:
            message: 用户消息
        
        Returns:
            回复字典
        """
        # 如果未初始化，先初始化
        if not self.agent:
            logger.info("Agent not initialized, attempting auto-initialization...")
            init_result = self.init_agent()
            if init_result.get("status") != "success":
                return {"status": "error", "message": f"Agent 初始化失败：{init_result.get('message')}"}
        
        if not self.agent:
            return {"status": "error", "message": "Agent 未初始化"}
        
        try:
            # 保存用户消息
            session_store.add_message("human", message, self.user_id)
            
            # 获取历史并转换为元组列表 [(role, content), ...]
            history_dicts = session_store.get_history(self.user_id, limit=10)
            # 从字典列表转换为元组列表，只取 role 和 content
            history: List[Tuple[str, str]] = [
                (item.get('role', ''), item.get('content', ''))
                for item in history_dicts
                if isinstance(item, dict) and 'role' in item and 'content' in item
            ]
            
            logger.debug(f"History converted: {len(history)} items")
            
            # 调用 Agent
            response = self.agent.chat(message, history)
            
            # 保存 AI 回复
            session_store.add_message("ai", response, self.user_id)
            
            return {
                "status": "success",
                "message": response,
                "emotion": "calm"
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "message": f"对话失败：{str(e)}"}
    
    def switch_model(self, provider: str) -> Dict[str, Any]:
        """切换模型"""
        if not self.agent:
            return {"status": "error", "message": "Agent 未初始化"}
        
        try:
            success = self.agent.switch_provider(provider)
            if success:
                return {"status": "success", "message": f"Switched to {provider}"}
            else:
                return {"status": "error", "message": "Switch failed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "status": "success",
            "agent_initialized": self.agent is not None,
            "user_id": self.user_id,
            "provider": self.agent.provider if self.agent else None
        }

# 主循环 - 通过 stdin/stdout 通信
def main():
    """主函数 - 处理来自 Electron 的消息"""
    bridge = BridgeService()
    logger.info("Bridge Service starting...")
    
    # 发送启动消息 - 使用 ensure_ascii=False
    try:
        print(json.dumps({"type": "ready", "message": "Bridge Service ready"}, ensure_ascii=False))
        sys.stdout.flush()
    except Exception as e:
        # 如果 UTF-8 失败，回退到 ASCII
        print(json.dumps({"type": "ready", "message": "Bridge Service ready"}, ensure_ascii=True))
        sys.stdout.flush()
    
    # 主循环
    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue
            
            data = json.loads(line)
            msg_type = data.get("type")
            payload = data.get("payload", {})
            
            logger.info(f"Received message type: {msg_type}")
            
            # 处理不同类型的消息
            if msg_type == "init":
                result = bridge.init_agent(payload.get("provider"))
            
            elif msg_type == "chat":
                result = bridge.chat(payload.get("message", ""))
            
            elif msg_type == "switch_model":
                result = bridge.switch_model(payload.get("provider"))
            
            elif msg_type == "status":
                result = bridge.get_status()
            
            else:
                result = {"status": "error", "message": f"Unknown message type: {msg_type}"}
            
            # 返回结果 - 使用 ensure_ascii=False
            try:
                response = {
                    "type": f"{msg_type}_response",
                    "data": result
                }
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except:
                # 如果包含 emoji 的消息失败，使用 ensure_ascii=True
                response = {
                    "type": f"{msg_type}_response",
                    "data": result
                }
                print(json.dumps(response, ensure_ascii=True))
                sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            try:
                error_response = {
                    "type": "error",
                    "data": {"status": "error", "message": str(e)}
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.stdout.flush()
            except:
                error_response = {
                    "type": "error",
                    "data": {"status": "error", "message": str(e)}
                }
                print(json.dumps(error_response, ensure_ascii=True))
                sys.stdout.flush()

if __name__ == "__main__":
    main()
