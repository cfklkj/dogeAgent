const fs = require('fs');
const path = require('path');

const chatPath = path.join(__dirname, 'electron', 'chat.html');
let content = fs.readFileSync(chatPath, 'utf-8');

// 找到旧的 processRecording 函数并替换
const oldFunc = 'async function processRecording(audioBlob)';
const newFunc = `async function processRecording(audioBlob) {
	console.log('[录音] 录音完成，大小:', audioBlob.size);
	
	// [语音优化] 使用 Web Speech API 进行语音识别
	const recognizedText = await recognizeSpeechFromBlob(audioBlob);
	
	const duration = (Date.now() - recordingStartTime) / 1000;
	
	if (recognizedText && recognizedText.trim()) {
		console.log('[录音] 识别成功:', recognizedText);
		addSystemMessage('🎤 识别结果："' + recognizedText + '"');
		userInput.value = recognizedText;
		setTimeout(() => {
			sendMessage();
		}, 500);
	} else {
		console.log('[录音] 识别失败');
		const durationSec = duration.toFixed(1);
		const placeholder = '[录音 ' + durationSec + '秒] ';
		userInput.value = placeholder + userInput.value;
		userInput.focus();
		addSystemMessage('⚠️ 语音识别失败，请手动输入内容后发送');
	}
}

// 语音识别辅助函数
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
		
		// 播放音频让浏览器识别
		const audio = new Audio(URL.createObjectURL(audioBlob));
		audio.play().catch(err => console.error('[语音] 播放失败:', err));
		
		setTimeout(() => {
			try { recognition.stop(); } catch(e) {}
			resolve(finalTranscript || null);
		}, 10000);
	});
}`;

// 找到函数定义并替换整个函数体
const startIdx = content.indexOf(oldFunc);
if (startIdx !== -1) {
	// 找到函数结束位置（下一个函数定义或注释）
	const endMarkers = ['// 录音按钮', 'toggleVoiceRecording', 'window.onload'];
	let endIdx = content.length;
	
	for (const marker of endMarkers) {
		const idx = content.indexOf(marker, startIdx + 100);
		if (idx !== -1 && idx < endIdx) {
			endIdx = idx;
		}
	}
	
	// 替换
	const before = content.substring(0, startIdx);
	const after = content.substring(endIdx);
	content = before + newFunc + '\n\n' + after;
	
	fs.writeFileSync(chatPath, content, 'utf-8');
	console.log('[OK] 已修复语音识别功能');
} else {
	console.log('[FAIL] 未找到 processRecording 函数');
}
