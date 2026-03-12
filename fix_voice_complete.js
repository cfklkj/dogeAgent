// 完整修复语音功能：播放 + 重录 + 识别
const fs = require('fs');
const path = require('path');

const chatPath = path.join(__dirname, 'electron', 'chat.html');
let content = fs.readFileSync(chatPath, 'utf-8');

// 1. 添加全局变量存储录音
const oldGlobals = 'let mediaRecorder = null;';
const newGlobals = `let mediaRecorder = null;
let lastRecordingBlob = null;  // 存储上一次的录音
let lastRecordingUrl = null;   // 上一次的音频 URL`;

if (content.includes(oldGlobals)) {
	content = content.replace(oldGlobals, newGlobals);
	console.log('[OK] 已添加全局变量');
}

// 2. 修改 ondataavailable 保存 blob
const oldData = 'audioChunks.push(event.data);';
const newData = `audioChunks.push(event.data);
// 实时更新 lastRecordingBlob
lastRecordingBlob = new Blob(audioChunks, { type: 'audio/webm' });`;

if (content.includes(oldData)) {
	content = content.replace(oldData, newData);
	console.log('[OK] 已添加 blob 保存');
}

// 3. 修改 onstop，添加播放和重录功能
const oldOnStop = `mediaRecorder.onstop = async () => {
	console.log('[录音] 录音停止');
	const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
	audioChunks = [];
	
	const duration = Date.now() - recordingStartTime;
	console.log(\`[录音] 录音时长：\${(duration / 1000).toFixed(2)}秒\`);
	
	// 转换为文本或使用 Web Speech API 进行识别
	await processRecording(audioBlob);
};`;

const newOnStop = `mediaRecorder.onstop = async () => {
	console.log('[录音] 录音停止');
	const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
	audioChunks = [];
	
	const duration = Date.now() - recordingStartTime;
	const durationSec = (duration / 1000).toFixed(2);
	console.log(\`[录音] 录音时长：\${durationSec}秒\`);
	
	// 保存最后一次录音
	lastRecordingBlob = audioBlob;
	if (lastRecordingUrl) {
		URL.revokeObjectURL(lastRecordingUrl);
	}
	lastRecordingUrl = URL.createObjectURL(audioBlob);
	
	// 显示播放控制
	showAudioControls(lastRecordingUrl, durationSec);
};`;

if (content.includes(oldOnStop)) {
	content = content.replace(oldOnStop, newOnStop);
	console.log('[OK] 已修改 onstop');
}

// 4. 添加播放控制 UI 函数
const showAudioControlsFunc = `
// 显示音频播放控制
function showAudioControls(audioUrl, duration) {
	const controlsHtml = \`
		<div class="audio-controls" style="margin: 10px; padding: 10px; background: rgba(255,255,255,0.9); border-radius: 8px;">
			<p>🎤 录音完成 (\${duration}秒)</p>
			<div style="display: flex; gap: 10px; margin-top: 8px;">
				<button onclick="playAudio('\${audioUrl}')" style="padding: 6px 12px; background: #48bb78; color: white; border: none; border-radius: 4px; cursor: pointer;">▶ 播放</button>
				<button onclick="reRecord()" style="padding: 6px 12px; background: #f56565; color: white; border: none; border-radius: 4px; cursor: pointer;">↻ 重录</button>
				<button onclick="sendRecognizedText()" style="padding: 6px 12px; background: #4299e1; color: white; border: none; border-radius: 4px; cursor: pointer;">✓ 识别并发送</button>
			</div>
		</div>
	\`;
	
	// 添加到聊天窗口
	const chatContainer = document.querySelector('.chat-container');
	const tempDiv = document.createElement('div');
	tempDiv.innerHTML = controlsHtml;
	chatContainer.appendChild(tempDiv);
	chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 播放音频
function playAudio(url) {
	const audio = new Audio(url);
	audio.play();
	console.log('[音频] 开始播放');
}

// 重录
function reRecord() {
	console.log('[录音] 重新录制');
	// 清除输入框
	userInput.value = '';
	// 移除控制条
	const controls = document.querySelector('.audio-controls');
	if (controls) controls.remove();
	// 重新开始录音
	toggleVoiceRecording();
}

// 识别并发送
async function sendRecognizedText() {
	if (!lastRecordingBlob) {
		console.error('[错误] 没有录音数据');
		return;
	}
	
	console.log('[录音] 开始识别...');
	const recognizedText = await recognizeSpeechFromBlob(lastRecordingBlob);
	
	if (recognizedText && recognizedText.trim()) {
		console.log('[录音] 识别成功:', recognizedText);
		addSystemMessage('🎤 识别结果："' + recognizedText + '"');
		userInput.value = recognizedText;
		// 移除控制条
		const controls = document.querySelector('.audio-controls');
		if (controls) controls.remove();
		// 发送
		setTimeout(() => {
			sendMessage();
		}, 500);
	} else {
		console.log('[录音] 识别失败');
		addSystemMessage('⚠️ 语音识别失败，请重试或手动输入');
	}
}

// 语音识别
async function recognizeSpeechFromBlob(audioBlob) {
	return new Promise((resolve, reject) => {
		const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
		
		if (!SpeechRecognition) {
			console.log('[语音] 浏览器不支持 SpeechRecognition API');
			resolve(null);
			return;
		}
		
		const recognition = new SpeechRecognition();
		recognition.lang = 'zh-CN';
		recognition.continuous = false;
		recognition.interimResults = true;
		
		let finalTranscript = '';
		
		recognition.onstart = () => {
			console.log('[语音] 开始识别...');
		};
		
		recognition.onresult = (event) => {
			let interimTranscript = '';
			for (let i = event.resultIndex; i < event.results.length; i++) {
				const transcript = event.results[i][0].transcript;
				if (event.results[i].isFinal) {
					finalTranscript += transcript;
				} else {
					interimTranscript += transcript;
				}
			}
			console.log('[语音] 识别中:', finalTranscript + interimTranscript);
		};
		
		recognition.onend = () => {
			console.log('[语音] 识别结束');
			resolve(finalTranscript || null);
		};
		
		recognition.onerror = (event) => {
			console.error('[语音] 识别错误:', event.error);
			resolve(null);
		};
		
		recognition.start();
		
		// 播放音频
		const audio = new Audio(URL.createObjectURL(audioBlob));
		audio.play().catch(err => console.error('[语音] 播放失败:', err));
		
		// 超时
		setTimeout(() => {
			try { recognition.stop(); } catch(e) {}
			resolve(finalTranscript || null);
		}, 10000);
	});
}
`;

// 在文件末尾添加函数
if (content.includes('</script>')) {
	content = content.replace('</script>', showAudioControlsFunc + '\n</script>');
	console.log('[OK] 已添加播放控制函数');
}

fs.writeFileSync(chatPath, content, 'utf-8');
console.log('[完成] 语音功能已修复');
