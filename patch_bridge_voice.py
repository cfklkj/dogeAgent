# 为 bridge.py 添加语音识别处理
import sys
sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)

with open('desktop/bridge.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在文件顶部添加导入
if 'from voice.speech_recognition import get_recognizer' not in content:
    import_section = '''from voice.speech_recognition import get_recognizer
from voice.text_to_speech import tts'''
    
    if 'from voice.text_to_speech import tts' in content:
        content = content.replace(
            'from voice.text_to_speech import tts',
            'from voice.speech_recognition import get_recognizer\nfrom voice.text_to_speech import tts'
        )
        print("[OK] 已添加语音识别导入")

# 在 handle_message 函数中添加语音识别处理
# 找到处理 chat 消息的部分
old_chat = '''elif msg_type == "chat":
            user_message = message.get("message", "")
            history = message.get("history", [])'''

new_chat = '''elif msg_type == "chat":
            # 检查是否是语音消息（包含音频数据）
            payload = message.get("payload", message)
            audio_data = payload.get("audio", None)
            user_message = payload.get("message", "")
            history = payload.get("history", [])
            
            # 如果有音频数据，先进行语音识别
            if audio_data:
                logger.info(f"[语音] 收到音频消息，大小：{len(audio_data)} 字节")
                try:
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    recognizer = get_recognizer("whisper")  # 使用 Whisper 引擎
                    recognized_text = await recognizer.recognize(audio_bytes, "zh-CN")
                    
                    if recognized_text:
                        logger.info(f"[语音] 识别结果：{recognized_text}")
                        user_message = recognized_text  # 使用识别结果作为用户消息
                        # 将识别结果推送给前端
                        send_response({
                            "type": "voice_recognized",
                            "text": recognized_text
                        })
                    else:
                        logger.warning("[语音] 识别失败")
                        send_response({
                            "type": "voice_error",
                            "message": "语音识别失败，请重试"
                        })
                        # 识别失败时不继续处理
                        continue
                except Exception as e:
                    logger.error(f"[语音] 识别错误：{e}", exc_info=True)
                    send_response({
                        "type": "voice_error",
                        "message": f"语音识别错误：{str(e)}"
                    })
                    continue'''

if old_chat in content:
    content = content.replace(old_chat, new_chat)
    with open('desktop/bridge.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] 已添加语音识别处理逻辑")
else:
    print("[FAIL] 未找到目标代码")
