"""
语音识别模块
"""
import asyncio
import logging
import queue
import threading
from typing import Optional, Callable, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class RecognitionEngine(Enum):
    """语音识别引擎类型"""
    LOCAL = "local"
    EDGE = "edge"
    WHISPER = "whisper"

class SpeechRecognizer:
    """语音识别器"""
    
    def __init__(self, engine: RecognitionEngine = RecognitionEngine.EDGE):
        self.engine = engine
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.callbacks = []
        logger.info(f"初始化语音识别器，引擎: {engine.value}")
    
    def start_listening(self, callback: Optional[Callable] = None):
        """开始监听"""
        if callback:
            self.callbacks.append(callback)
        if self.is_listening:
            return
        
        self.is_listening = True
        logger.info("开始语音监听")
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        logger.info("停止语音监听")
    
    async def recognize(self, audio_data: bytes) -> Optional[str]:
        """识别音频"""
        # 简化版：返回模拟结果
        import random
        phrases = ["今天天气怎么样", "现在几点了", "给我讲个笑话", "你好呀"]
        return random.choice(phrases)

class WakeWordDetector:
    """唤醒词检测器"""
    
    def __init__(self, wake_words: list = ["小狗", "doge", "嘿小狗"]):
        self.wake_words = [w.lower() for w in wake_words]
        self.callbacks = []
        logger.info(f"唤醒词检测器初始化，唤醒词: {wake_words}")
    
    def detect(self, text: str) -> bool:
        """检测是否包含唤醒词"""
        text_lower = text.lower()
        for word in self.wake_words:
            if word in text_lower:
                logger.info(f"检测到唤醒词: {word}")
                for callback in self.callbacks:
                    try:
                        callback(word)
                    except Exception as e:
                        logger.error(f"唤醒回调失败: {e}")
                return True
        return False
    
    def add_callback(self, callback: Callable):
        """添加唤醒回调"""
        self.callbacks.append(callback)
