"""
文本转语音模块
"""
import os
import logging
import tempfile
import hashlib
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)

class TTSEngine(Enum):
    """语音合成引擎类型"""
    EDGE = "edge"
    SYSTEM = "system"

class VoiceType(Enum):
    """声音类型"""
    CUTE = "cute"
    GENTLE = "gentle"
    CHEERFUL = "cheerful"

class TextToSpeech:
    """文本转语音合成器"""
    
    def __init__(self, engine: TTSEngine = TTSEngine.EDGE):
        self.engine = engine
        self.cache_dir = "assets/sounds/tts_cache"
        self.voice_type = VoiceType.CUTE
        self.speed = 1.0
        self.volume = 0.8
        
        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info(f"初始化TTS，引擎: {engine.value}")
        self._init_engine()
    
    def _init_engine(self):
        """初始化TTS引擎"""
        try:
            if self.engine == TTSEngine.EDGE:
                self._init_edge()
            else:
                self._init_system()
        except Exception as e:
            logger.error(f"初始化TTS引擎失败: {e}")
            self.engine = TTSEngine.SYSTEM
    
    def _init_edge(self):
        """初始化Edge-TTS"""
        try:
            import edge_tts
            self.edge_voice = "zh-CN-XiaoxiaoNeural"
            logger.info(f"Edge-TTS初始化成功")
        except ImportError:
            logger.warning("Edge-TTS未安装，使用系统TTS")
            self.engine = TTSEngine.SYSTEM
    
    def _init_system(self):
        """初始化系统TTS"""
        try:
            import pyttsx3
            self.system_engine = pyttsx3.init()
            self.system_engine.setProperty('rate', 150)
            self.system_engine.setProperty('volume', self.volume)
            logger.info("系统TTS初始化成功")
        except ImportError:
            logger.warning("pyttsx3未安装")
    
    def _get_cache_path(self, text: str) -> str:
        """获取缓存文件路径"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{text_hash}.mp3")
    
    async def synthesize(self, text: str, play: bool = True) -> Optional[str]:
        """合成语音"""
        cache_path = self._get_cache_path(text)
        
        if os.path.exists(cache_path):
            logger.debug(f"使用缓存语音: {cache_path}")
            if play:
                self.play(cache_path)
            return cache_path
        
        try:
            if self.engine == TTSEngine.EDGE:
                audio_file = await self._synthesize_edge(text, cache_path)
            else:
                audio_file = self._synthesize_system(text, cache_path)
            
            if play and audio_file:
                self.play(audio_file)
            
            return audio_file
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            return None
    
    async def _synthesize_edge(self, text: str, output_path: str) -> str:
        """使用Edge-TTS合成"""
        import edge_tts
        communicate = edge_tts.Communicate(text, self.edge_voice)
        await communicate.save(output_path)
        return output_path
    
    def _synthesize_system(self, text: str, output_path: str) -> str:
        """使用系统TTS合成"""
        self.system_engine.save_to_file(text, output_path)
        self.system_engine.runAndWait()
        return output_path
    
    def play(self, audio_file: str):
        """播放音频"""
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except Exception as e:
            logger.error(f"播放音频失败: {e}")
    
    def stop(self):
        """停止播放"""
        try:
            import pygame
            pygame.mixer.music.stop()
        except:
            pass

# 全局 TTS 实例
_tts_instance: Optional[TextToSpeech] = None

def get_tts() -> TextToSpeech:
    """获取全局 TTS 实例"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech()
    return _tts_instance
