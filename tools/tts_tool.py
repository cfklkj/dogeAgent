"""
文字转语音工具 - 使用 Edge TTS
支持多种语言和音色
添加重试机制和错误处理
"""
import asyncio
import os
import logging
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger("dogeAgent.tools.tts")

# Edge TTS 支持的中文语音
CHINESE_VOICES = [
    "zh-CN-YunxiNeural",  # 男声
    "zh-CN-XiaoxiaoNeural",  # 温暖女声
    "zh-CN-YunyangNeural",  # 专业男声
]

async def text_to_speech_async(
    text: str,
    output_file: str,
    voice: str = "zh-CN-YunxiNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz",
    retry_count: int = 3
) -> str:
    """
    异步文字转语音（带重试机制）
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径
        voice: 语音音色
        rate: 语速
        pitch: 音调
        retry_count: 重试次数
    
    Returns:
        输出文件路径
    """
    start_time = time.time()
    last_error = None
    
    for attempt in range(retry_count):
        try:
            import edge_tts
            
            logger.info(f"[TTS 尝试 {attempt+1}/{retry_count}] 文本：{text[:50]}... 音色：{voice}")
            
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_file)
            
            # 验证文件
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                duration = time.time() - start_time
                logger.info(f"[TTS 成功] 文件：{output_file}, 大小：{file_size}字节，耗时：{duration:.2f}秒")
                return output_file
            else:
                logger.error(f"[TTS 失败] 文件未生成：{output_file}")
                
        except Exception as e:
            last_error = e
            logger.warning(f"[TTS 失败 {attempt+1}/{retry_count}] {e}")
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 1  # 递增等待时间
                logger.info(f"等待 {wait_time}秒后重试...")
                await asyncio.sleep(wait_time)
    
    # 所有重试都失败
    logger.error(f"[TTS 最终失败] 所有重试完成，错误：{last_error}")
    if last_error:
        raise last_error
    raise RuntimeError("TTS 转换失败")

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
        logger.info(f"[TTS 同步调用] 开始转换...")
        return asyncio.run(text_to_speech_async(text, output_file, voice, rate, pitch))
    except Exception as e:
        logger.error(f"[TTS 同步错误] {e}", exc_info=True)
        # 返回一个空的或备用文件
        raise

def get_available_voices() -> list:
    """
    获取可用的中文语音列表
    
    Returns:
        语音列表
    """
    return [
        {"name": "zh-CN-YunxiNeural", "gender": "男声", "description": "标准男声"},
        {"name": "zh-CN-XiaoxiaoNeural", "gender": "女声", "description": "温暖女声"},
        {"name": "zh-CN-YunyangNeural", "gender": "男声", "description": "专业男声"},
    ]

# 测试函数
if __name__ == "__main__":
    output = "test_output.mp3"
    print(f"测试 TTS，输出文件：{output}")
    result = text_to_speech("你好，我是你的柴犬助手 Doge!", output)
    print(f"生成成功：{result}")
