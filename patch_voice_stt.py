# 为 chat.html 添加语音识别补丁
import sys
sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)

with open('electron/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在录音结束处理函数中，添加语音识别逻辑
# 找到处理录音完成的代码
old_code = '''// 处理录音完成
function handleRecordingComplete(blob, duration) {
    const audioUrl = URL.createObjectURL(blob);
    addSystemMessage(`录音完成，时长 ${duration} 秒`);
    // TODO: 发送到后端进行语音识别
}'''

new_code = '''// 处理录音完成
async function handleRecordingComplete(blob, duration) {
    const audioUrl = URL.createObjectURL(blob);
    
    // [语音优化] 先进行语音识别
    const recognizedText = await recognizeSpeech(blob);
    
    if (recognizedText && recognizedText.trim()) {
        addSystemMessage(`识别结果："${recognizedText}"`);
        // 将识别结果作为用户消息发送
        userInput.value = recognizedText;
        sendMessage();
    } else {
        addSystemMessage('语音识别失败，请重试或使用文字输入');
    }
}

// 语音识别函数（使用 Web Speech API）
async function recognizeSpeech(audioBlob) {
    return new Promise((resolve, reject) => {
        // 检查浏览器支持
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.log('浏览器不支持语音识别，使用备用方案');
            resolve(null);
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'zh-CN';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            console.log('语音识别开始...');
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('语音识别结果:', transcript);
            resolve(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('语音识别错误:', event.error);
            resolve(null);
        };
        
        recognition.onend = () => {
            console.log('语音识别结束');
        };
        
        // 开始识别
        recognition.start();
        
        // 3 秒后自动停止（超时保护）
        setTimeout(() => {
            try {
                recognition.stop();
            } catch (e) {
                console.log('识别已停止');
            }
        }, 10000);
    });
}'''

if '// 处理录音完成' in content and 'function handleRecordingComplete' in content:
    # 找到函数定义并替换
    import re
    # 使用正则表达式匹配整个函数
    pattern = r'function handleRecordingComplete\(blob, duration\) \{[^}]*// TODO: 发送到后端进行语音识别[^}]*\}'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_code.split('async')[0] + 'async ' + new_code.split('async')[1], content, flags=re.DOTALL)
        with open('electron/chat.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] 已添加语音识别逻辑（方案 1：正则替换）")
    else:
        print("[INFO] 未找到 TODO 注释，尝试其他方法")
        # 直接查找函数定义
        if 'function handleRecordingComplete(blob, duration)' in content:
            print("找到函数定义，但格式不同")
else:
    print("[FAIL] 未找到 handleRecordingComplete 函数")
    print("可能需要手动添加或检查 chat.html 结构")
