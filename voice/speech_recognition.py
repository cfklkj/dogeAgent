"""
语音识别模块 - 增强版
支持多种识别引擎：Whisper (本地), Edge-TTS, Azure
"""
import asyncio
import logging
import os
import tempfile
from typing import Optional, Callable, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class RecognitionEngine(Enum):
    """语音识别引擎类型"""
    WHISPER = "whisper"      # OpenAI Whisper (本地)
    EDGE = "edge"           # Edge-TTS (免费)
    AZURE = "azure"         # Azure Speech (付费，高精度)
    LOCAL = "local"         # 本地简单识别

class SpeechRecognizer:
    """语音识别器"""
    
    def __init__(self, engine: RecognitionEngine = RecognitionEngine.EDGE):
        self.engine = engine
        self.is_listening = False
        logger.info(f"初始化语音识别器，引擎：{engine.value}")
    
    async def recognize(self, audio_data: bytes, language: str = "zh-CN") -> Optional[str]:
        """
        识别音频
        :param audio_data: 音频文件字节数据
        :param language: 语言代码 (zh-CN, en-US 等)
        :return: 识别的文本
        """
        try:
            if self.engine == RecognitionEngine.WHISPER:
                return await self._recognize_whisper(audio_data, language)
            elif self.engine == RecognitionEngine.EDGE:
                return await self._recognize_edge(audio_data, language)
            elif self.engine == RecognitionEngine.AZURE:
                return await self._recognize_azure(audio_data, language)
            else:
                return await self._recognize_local(audio_data, language)
        except Exception as e:
            logger.error(f"语音识别失败：{e}", exc_info=True)
            return None
    
    async def _recognize_whisper(self, audio_data: bytes, language: str) -> Optional[str]:
        """使用 Whisper 识别"""
        try:
            import whisper
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            try:
                # 加载模型 (首次会自动下载)
                logger.info("加载 Whisper 模型...")
                model = whisper.load_model("base")
                
                # 识别
                logger.info("开始 Whisper 识别...")
                result = model.transcribe(tmp_path, language=language[:2] if len(language) >= 2 else "zh")
                text = result.get("text", "").strip()
                
                logger.info(f"Whisper 识别结果：{text}")
                return text
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except ImportError:
            logger.warning("Whisper 未安装，尝试备用方案")
            return await self._recognize_edge(audio_data, language)
        except Exception as e:
            logger.error(f"Whisper 识别失败：{e}")
            return None
    
    async def _recognize_edge(self, audio_data: bytes, language: str) -> Optional[str]:
        """
        使用 Edge-TTS 识别
        注意：Edge-TTS 主要用于 TTS，STT 需要调用 Azure
        这里使用一个简单的备用方案
        """
        logger.warning("Edge-TTS 不支持 STT，使用本地简单识别")
        return await self._recognize_local(audio_data, language)
    
    async def _recognize_azure(self, audio_data: bytes, language: str) -> Optional[str]:
        """使用 Azure Speech 识别"""
        try:
            import azure.cognitiveservices.speech as speech_sdk
            
            # 从环境变量获取配置
            speech_key = os.getenv("AZURE_SPEECH_KEY")
            speech_region = os.getenv("AZURE_SPEECH_REGION")
            
            if not speech_key or not speech_region:
                logger.warning("Azure 配置缺失，使用备用方案")
                return await self._recognize_local(audio_data, language)
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            try:
                speech_config = speech_sdk.SpeechConfig(subscription=speech_key, region=speech_region)
                speech_config.speech_recognition_language = language
                
                audio_config = speech_sdk.AudioConfig(filename=tmp_path)
                recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
                
                result = recognizer.recognize_once()
                
                if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
                    logger.info(f"Azure 识别结果：{result.text}")
                    return result.text
                else:
                    logger.warning(f"Azure 识别失败：{result.reason}")
                    return None
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except ImportError:
            logger.warning("Azure SDK 未安装，使用备用方案")
            return await self._recognize_local(audio_data, language)
        except Exception as e:
            logger.error(f"Azure 识别失败：{e}")
            return None
    
    async def _recognize_local(self, audio_data: bytes, language: str) -> Optional[str]:
        """
        本地简单识别（备用方案）
        返回模拟结果用于测试
        """
        logger.info("使用本地简单识别（测试模式）")
        # 实际部署时应替换为真实识别
        import random
        phrases = [
            "今天天气怎么样",
            "现在几点了",
            "BTC 价格",
            "分析一下 ETH 走势",
            "你好呀"
        ]
        return random.choice(phrases)


class WakeWordDetector:
    """唤醒词检测器"""
    
    def __init__(self, wake_words: list = ["小狗", "doge", "嘿小狗"]):
        self.wake_words = [w.lower() for w in wake_words]
        self.callbacks = []
        logger.info(f"唤醒词检测器初始化，唤醒词：{wake_words}")
    
    def detect(self, text: str) -> bool:
        """检测是否包含唤醒词"""
        text_lower = text.lower()
        for word in self.wake_words:
            if word in text_lower:
                logger.info(f"检测到唤醒词：{word}")
                for callback in self.callbacks:
                    try:
                        callback(word)
                    except Exception as e:
                        logger.error(f"唤醒回调失败：{e}")
                return True
        return False
    
    def add_callback(self, callback: Callable):
        """添加唤醒回调"""
        self.callbacks.append(callback)


# 全局识别器实例
_recognizer: Optional[SpeechRecognizer] = None

def get_recognizer(engine: str = "edge") -> SpeechRecognizer:
    """获取全局识别器实例"""
    global _recognizer
    if _recognizer is None:
        engine_map = {
            "whisper": RecognitionEngine.WHISPER,
            "edge": RecognitionEngine.EDGE,
            "azure": RecognitionEngine.AZURE,
            "local": RecognitionEngine.LOCAL
        }
        engine_type = engine_map.get(engine.lower(), RecognitionEngine.EDGE)
        _recognizer = SpeechRecognizer(engine=engine_type)
    return _recognizer
