"""
桥接服务 - Electron 与 Python 之间的通信
注意：所有输出使用 UTF-8 编码，避免 Windows GBK 问题
"""
import sys
import os
import json
import logging
import io
import tempfile
import time
import base64
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
        
        # 设置状态变化回调
        state = get_state_manager()
        state.set_on_status_change(self._on_status_change)
        
        logger.info("Bridge Service initialized")
    
    def _on_status_change(self, old_status: str, new_status: str):
        """
        状态变化回调函数
        
        Args:
            old_status: 旧状态
            new_status: 新状态
        """
        logger.info(f"[状态回调] {old_status} -> {new_status}")
        # 状态变化时主动推送
        self._push_status_update()
    
    def _push_status_update(self):
        """主动推送状态更新"""
        try:
            state = get_state_manager()
            status_dict = state.get_status_dict()
            current_status = status_dict.get('status')
            
            # 更新 last_status 以便后续检测变化
            self.last_status = current_status
            
            logger.info(f"[状态推送] {current_status}")
            send_response({
                "type": "status_update",
                "data": {
                    "status": "success",
                    "data": status_dict
                }
            })
        except Exception as e:
            logger.error(f"[状态推送失败] {e}")
    
    def init_agent(self, provider: str = None) -> Dict[str, Any]:
        """初始化 Agent"""
        try:
            logger.info(f"[初始化] 开始初始化 Agent, provider: {provider}")
            self.provider = provider
            self.agent = get_agent(provider)
            logger.info("Agent 初始化成功")
            
            # 初始化完成后，推送一次状态
            self._push_status_update()
            
            return {
                "status": "success",
                "message": "Agent 初始化成功"
            }
        except Exception as e:
            logger.error(f"[初始化失败] {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Agent 初始化失败：{str(e)}"
            }
    
    def chat(self, message: str, history: List[Tuple[str, str]] = None) -> Dict[str, Any]:
        """与 Agent 对话"""
        try:
            if not self.agent:
                logger.warning("Agent 未初始化，自动初始化...")
                self.init_agent()
            
            logger.info(f"[聊天] 收到消息：{message[:50]}...")
            response = self.agent.chat(message, history)
            logger.info(f"[聊天] 回复：{response[:50]}...")
            
            return {
                "status": "success",
                "response": response
            }
        except Exception as e:
            logger.error(f"[聊天失败] {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"对话失败：{str(e)}"
            }
    
    def text_to_speech(self, text: str, voice: str = "zh-CN-YunxiNeural") -> Dict[str, Any]:
        """
        文字转语音（返回 Base64 编码的音频数据）
        
        Args:
            text: 要转换的文本
            voice: 语音音色
        
        Returns:
            包含音频 Base64 数据的字典
        """
        start_time = time.time()
        logger.info(f"[TTS 请求] 开始处理，文本：{text[:50]}..., 音色：{voice}")
        
        try:
            from tools.tts_tool import text_to_speech as tts
            
            # 生成临时文件
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time() * 1000)
            output_file = os.path.join(temp_dir, f"doge_tts_{timestamp}.mp3")
            
            logger.info(f"[TTS] 输出文件：{output_file}")
            
            # 调用 TTS
            tts(text, output_file, voice=voice)
            
            # 读取文件并转换为 Base64
            if os.path.exists(output_file):
                with open(output_file, 'rb') as f:
                    audio_data = f.read()
                
                file_size = len(audio_data)
                
                # 检查文件大小
                if file_size < 100:
                    logger.error(f"[TTS 失败] 文件太小：{file_size} 字节，可能是空音频")
                    return {
                        "status": "error",
                        "message": "TTS 生成的音频文件为空"
                    }
                
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                duration = time.time() - start_time
                
                logger.info(f"[TTS 完成] 大小：{file_size}字节，Base64 长度：{len(audio_base64)}, 耗时：{duration:.2f}秒")
                
                # 清理临时文件
                try:
                    os.remove(output_file)
                    logger.debug(f"[TTS] 清理临时文件：{output_file}")
                except Exception as e:
                    logger.warning(f"[TTS] 清理文件失败：{e}")
                
                return {
                    "status": "success",
                    "audio_base64": audio_base64,
                    "text": text,
                    "file_size": file_size,
                    "mime_type": "audio/mpeg"
                }
            else:
                logger.error(f"[TTS 失败] 文件未生成：{output_file}")
                return {
                    "status": "error",
                    "message": "TTS 文件未生成"
                }
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[TTS 失败] 耗时：{duration:.2f}秒，错误：{e}", exc_info=True)
            # 返回错误信息，前端使用浏览器原生 TTS
            return {
                "status": "error",
                "message": f"TTS 失败：{str(e)}",
                "fallback": True  # 标记使用浏览器原生 TTS
            }
    
    def switch_provider(self, provider: str) -> Dict[str, Any]:
        """切换模型提供商"""
        try:
            if not self.agent:
                return {
                    "status": "error",
                    "message": "Agent 未初始化"
                }
            
            logger.info(f"[切换] 切换到：{provider}")
            success = self.agent.switch_provider(provider)
            
            if success:
                logger.info(f"[切换成功] {provider}")
                # 切换后推送状态
                self._push_status_update()
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
            logger.error(f"[切换失败] {e}", exc_info=True)
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
                logger.debug(f"[状态查询] 状态变化：{current_status}")
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
            logger.error(f"[状态查询失败] {e}", exc_info=True)
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
        logger.info(f"[状态变化通知] {old_status} -> {new_status}")
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
            logger.error(f"[状态通知失败] {e}")

def send_response(response: Dict[str, Any]):
    """发送响应到 Electron"""
    try:
        # 确保使用 UTF-8 编码
        json_str = json.dumps(response, ensure_ascii=False)
        logger.debug(f"[发送] {json_str[:100]}...")
        # 直接输出 UTF-8 字符串
        print(json_str, flush=True)
    except Exception as e:
        logger.error(f"[发送失败] {e}", exc_info=True)

def process_message(service: BridgeService, message: Dict[str, Any]):
    """处理接收到的消息"""
    try:
        msg_type = message.get("type")
        logger.info(f"[接收] 类型：{msg_type}")
        
        if msg_type == "init":
            provider = message.get("provider")
            result = service.init_agent(provider)
            send_response({"type": "init_response", "data": result})
        
        elif msg_type == "chat":
            user_message = message.get("message", "")
            history = message.get("history", [])
            result = service.chat(user_message, history)
            send_response({"type": "chat_response", "data": result})
        
        elif msg_type == "tts":
            text = message.get("text", "")
            voice = message.get("voice", "zh-CN-YunxiNeural")
            logger.info(f"[TTS 请求] 文本：{text[:50]}..., 音色：{voice}")
            result = service.text_to_speech(text, voice)
            send_response({"type": "tts_response", "data": result})
        
        elif msg_type == "switch_provider":
            provider = message.get("provider")
            result = service.switch_provider(provider)
            send_response({"type": "switch_response", "data": result})
        
        elif msg_type == "get_status":
            result = service.get_status()
            send_response({"type": "status_response", "data": result})
        
        else:
            logger.warning(f"[未知类型] {msg_type}")
            send_response({
                "type": "error",
                "data": {"message": f"未知消息类型：{msg_type}"}
            })
    
    except Exception as e:
        logger.error(f"[处理错误] {e}", exc_info=True)
        send_response({
            "type": "error",
            "data": {"message": f"处理消息失败：{str(e)}"}
        })

def main():
    """主函数"""
    logger.info("Bridge Service 启动...")
    
    try:
        service = BridgeService()
        logger.info("Bridge Service 就绪")
        
        # 发送就绪信号
        send_response({"type": "ready", "message": "Bridge Service ready"})
        
        # 主循环
        for line in sys.stdin:
            try:
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"[原始输入] {line[:100]}...")
                message = json.loads(line)
                process_message(service, message)
            
            except json.JSONDecodeError as e:
                logger.error(f"[JSON 错误] {e}")
                send_response({
                    "type": "error",
                    "data": {"message": f"JSON 解析错误：{str(e)}"}
                })
            except Exception as e:
                logger.error(f"[主循环错误] {e}", exc_info=True)
                send_response({
                    "type": "error",
                    "data": {"message": f"主循环错误：{str(e)}"}
                })
    
    except KeyboardInterrupt:
        logger.info("Bridge Service 被用户中断")
    except Exception as e:
        logger.error(f"[致命错误] {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
