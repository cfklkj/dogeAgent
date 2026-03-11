"""
文字转语音工具 - 使用 Edge TTS
支持多种语言和音色
"""
import asyncio
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("dogeAgent.tools.tts")

# Edge TTS 支持的中文语音
# zh-CN-YunxiNeural - 男声
# zh-CN-YunxiNeural - 女声
# zh-CN-XiaoxiaoNeural - 女声（温暖）
# zh-CN-YunyangNeural - 男声（专业）

async def text_to_speech_async(
    text: str,
    output_file: str,
    voice: str = "zh-CN-YunxiNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> str:
    """
    异步文字转语音
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径
        voice: 语音音色，默认 zh-CN-YunxiNeural
        rate: 语速，如 "+0%", "-10%", "+10%"
        pitch: 音调，如 "+0Hz", "-10Hz", "+10Hz"
    
    Returns:
        输出文件路径
    """
    try:
        import edge_tts
        
        logger.info(f"开始 TTS 转换：{text[:50]}...")
        
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_file)
        
        logger.info(f"TTS 完成：{output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"TTS 转换失败：{e}", exc_info=True)
        raise

def text_to_speech(
    text: str,
    output_file: str,
    voice: str = "zh-CN-YunxiNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> str:
    """
    同步文字转语音（包装异步版本）
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径
        voice: 语音音色
        rate: 语速
        pitch: 音调
    
    Returns:
        输出文件路径
    """
    try:
        return asyncio.run(text_to_speech_async(text, output_file, voice, rate, pitch))
    except Exception as e:
        logger.error(f"TTS 转换失败：{e}", exc_info=True)
        raise

def get_available_voices() -> list:
    """
    获取可用的中文语音列表
    
    Returns:
        语音列表
    """
    return [
        {"name": "zh-CN-YunxiNeural", "gender": "男声", "description": "标准男声"},
        {"name": "zh-CN-YunxiNeural", "gender": "女声", "description": "标准女声"},
        {"name": "zh-CN-XiaoxiaoNeural", "gender": "女声", "description": "温暖女声"},
        {"name": "zh-CN-YunyangNeural", "gender": "男声", "description": "专业男声"},
        {"name": "zh-CN-liaoning-XiaobeiNeural", "gender": "女声", "description": "东北口音"},
    ]

# 测试函数
if __name__ == "__main__":
    output = "test_output.mp3"
    result = text_to_speech("你好，我是你的柴犬助手 Doge！", output)
    print(f"生成成功：{result}")
