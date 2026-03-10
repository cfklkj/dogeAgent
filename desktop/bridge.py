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

# 在导入其他模块之前先初始化日志
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import get_doge_logger, create_module_logger

# 初始化日志
logger = create_module_logger("bridge")

# ============================================================================
# 关键修复：强制设置标准输出为 UTF-8
# Windows 默认 GBK 编码会导致中文和 emoji 乱码
# ============================================================================
if sys.platform == 'win32':
    # 重新编码 stdout 和 stderr 为 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def clean_text(text: str) -> str:
    """
    清理文本中的无效 UTF-8 字符（如 UTF-16 代理对）
    """
    if not text:
        return ""
    try:
        # 尝试编码为 UTF-8，如果有代理对会失败
        text.encode('utf-8')
        return text
    except (UnicodeEncodeError, UnicodeDecodeError):
        # 使用 'surrogatepass' 处理代理对，然后替换为空白
        cleaned = text.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='surrogatepass')
        # 再次尝试清理
        try:
            cleaned.encode('utf-8')
            return cleaned
        except:
            # 如果还是失败，替换所有无效字符
            return text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')

# 添加项目根目录到 Python 路径
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / '.env')

# 现在可以正确导入项目模块
from agent.factory import get_agent, reset_agent
from agent.status import get_state_manager

class BridgeService:
    """桥接服务类"""
    
    def __init__(self):
        self.agent = None
        self.provider = None
        self.last_status = None  # 记录上次发送的状态，避免重复发送
        logger.info("Bridge Service initialized")
    
    def init_agent(self, provider: str = None) -> Dict[str, Any]:
        """初始化 Agent"""
        try:
            logger.info(f"Starting to initialize Agent, provider: {provider}")
            self.provider = provider
            self.agent = get_agent(provider)
            logger.info("Agent initialized successfully")
            return {
                "status": "success",
                "message": "Agent 初始化成功"
            }
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Agent 初始化失败：{str(e)}"
            }
    
    def chat(self, message: str, history: List[Tuple[str, str]] = None) -> Dict[str, Any]:
        """与 Agent 对话"""
        try:
            if not self.agent:
                logger.warning("Agent not initialized, auto-initializing...")
                self.init_agent()
            
            logger.info(f"Processing message: {message[:50]}...")
            response = self.agent.chat(message, history)
            logger.info(f"Response generated: {response[:50]}...")
            
            return {
                "status": "success",
                "response": response
            }
        except Exception as e:
            logger.error(f"Chat failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"对话失败：{str(e)}"
            }
    
    def switch_provider(self, provider: str) -> Dict[str, Any]:
        """切换模型提供商"""
        try:
            if not self.agent:
                return {
                    "status": "error",
                    "message": "Agent 未初始化"
                }
            
            logger.info(f"Switching provider to: {provider}")
            success = self.agent.switch_provider(provider)
            
            if success:
                logger.info(f"Provider switched to: {provider}")
                return {
                    "status": "success",
                    "message": f"已切换到 {provider}"
                }
            else:
                return {
                    "status": "error",
                    "message": "切换失败"
                }
        except Exception as e:
            logger.error(f"Switch provider failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取 Agent 状态"""
        try:
            state = get_state_manager()
            status_dict = state.get_status_dict()
            
            # 检查状态是否变化，避免重复发送
            current_status = status_dict.get('status')
            if current_status != self.last_status:
                self.last_status = current_status
                logger.debug(f"状态变化：{current_status}")
                # 主动推送状态更新
                send_response({
                    "type": "status_update",
                    "data": {
                        "status": "success",
                        "data": status_dict
                    }
                })
            
            return {
                "status": "success",
                "data": status_dict
            }
        except Exception as e:
            logger.error(f"Get status failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"获取状态失败：{str(e)}"
            }
    
    def notify_status_change(self, old_status: str, new_status: str):
        """
        当状态变化时主动通知前端
        
        Args:
            old_status: 旧状态
            new_status: 新状态
        """
        logger.info(f"状态变化通知：{old_status} -> {new_status}")
        try:
            state = get_state_manager()
            status_dict = state.get_status_dict()
            send_response({
                "type": "status_update",
                "data": {
                    "status": "success",
                    "data": status_dict
                }
            })
        except Exception as e:
            logger.error(f"发送状态变化通知失败：{e}")

def send_response(response: Dict[str, Any]):
    """发送响应到 Electron"""
    try:
        # 确保使用 UTF-8 编码
        json_str = json.dumps(response, ensure_ascii=False)
        logger.debug(f"Sending response: {json_str[:100]}...")
        # 直接输出 UTF-8 字符串
        print(json_str, flush=True)
    except Exception as e:
        logger.error(f"Failed to send response: {e}", exc_info=True)

def process_message(service: BridgeService, message: Dict[str, Any]):
    """处理接收到的消息"""
    try:
        msg_type = message.get("type")
        logger.info(f"Received message type: {msg_type}")
        
        if msg_type == "init":
            provider = message.get("provider")
            result = service.init_agent(provider)
            send_response({"type": "init_response", "data": result})
        
        elif msg_type == "chat":
            user_message = message.get("message", "")
            history = message.get("history", [])
            result = service.chat(user_message, history)
            send_response({"type": "chat_response", "data": result})
        
        elif msg_type == "switch_provider":
            provider = message.get("provider")
            result = service.switch_provider(provider)
            send_response({"type": "switch_response", "data": result})
        
        elif msg_type == "get_status":
            result = service.get_status()
            send_response({"type": "status_response", "data": result})
        
        else:
            logger.warning(f"Unknown message type: {msg_type}")
            send_response({
                "type": "error",
                "data": {"message": f"未知消息类型：{msg_type}"}
            })
    
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        send_response({
            "type": "error",
            "data": {"message": f"处理消息失败：{str(e)}"}
        })

def main():
    """主函数"""
    logger.info("Bridge Service starting...")
    
    try:
        service = BridgeService()
        logger.info("Bridge Service ready")
        
        # 发送就绪信号
        send_response({"type": "ready", "message": "Bridge Service ready"})
        
        # 主循环
        for line in sys.stdin:
            try:
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"Received raw input: {line[:100]}...")
                message = json.loads(line)
                process_message(service, message)
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                send_response({
                    "type": "error",
                    "data": {"message": f"JSON 解析错误：{str(e)}"}
                })
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                send_response({
                    "type": "error",
                    "data": {"message": f"主循环错误：{str(e)}"}
                })
    
    except KeyboardInterrupt:
        logger.info("Bridge Service stopped by user")
    except Exception as e:
        logger.error(f"Bridge Service fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
