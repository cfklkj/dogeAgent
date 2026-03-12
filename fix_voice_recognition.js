// 修复语音识别功能
const fs = require('fs');
const path = require('path');

const chatPath = path.join(__dirname, 'electron', 'chat.html');
let content = fs.readFileSync(chatPath, 'utf-8');

// 找到 processRecording 函数
const oldProcessRecording = `async function processRecording(audioBlob) {
	// 简单方法直接使用浏览器语音识别
	// 如果需要更准确的识别，可以上传音频文件到服务器
	
	console.log('[录音] 录音完成，大小:', audioBlob.size);
	
	// 简单方法，直接使用浏览器的简单识别
	// 1. 显示录音时长
	// 2. 提示用户自己输入文字
	const duration = (Date.now() - recordingStartTime) / 1000;
	const placeholder = `[录音 ${duration.toFixed(1)}秒] `;
	userInput.value = placeholder + userInput.value;
	userInput.focus();
	
	// 简单方法，提示用户自己修改文字，然后发送
	console.log('[录音] 请使用输入法输入文字，然后发送录音');
}`;

const newProcessRecording = `async function processRecording(audioBlob) {
	console.log('[录音] 录音完成，大小:', audioBlob.size);
	
	// [语音优化] 使用 Web Speech API 进行语音识别
	const recognizedText = await recognizeSpeechFromBlob(audioBlob);
	
	const duration = (Date.now() - recordingStartTime) / 1000;
	
	if (recognizedText && recognizedText.trim()) {
		console.log('[录音] 识别成功:', recognizedText);
		addSystemMessage('🎤 识别结果："' + recognizedText + '"');
		// 将识别结果填入输入框并发送
		userInput.value = recognizedText;
		setTimeout(() => {
			sendMessage();
		}, 500);
	} else {
		console.log('[录音] 识别失败，使用占位符');
		const placeholder = \`[录音 \${duration.toFixed(1)}秒] \`;
		userInput.value = placeholder + userInput.value;
		userInput.focus();
		addSystemMessage('⚠️ 语音识别失败，请手动输入内容后发送');
	}
}

// 语音识别函数
async function recognizeSpeechFromBlob(audioBlob) {
	return new Promise((resolve, reject) => {
		// 检查浏览器支持
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
		
		// 开始识别
		recognition.start();
		
		// 注意：Web Speech API 通常用于实时语音，而不是录音文件
		// 这里我们只是启动识别，实际应该将音频文件传给识别引擎
		// 但由于浏览器限制，无法直接将 Blob 传给 SpeechRecognition
		// 所以我们采用一个变通方法：播放音频并让浏览器实时识别
		
			// 创建音频元素并播放
		const audio = new Audio(URL.createObjectURL(audioBlob));
		audio.play().catch(err => {
			console.error('[语音] 播放失败:', err);
			resolve(null);
		});
		
		// 10 秒后超时
		setTimeout(() => {
			try {
				recognition.stop();
			} catch (e) {}
			resolve(finalTranscript || null);
		}, 10000);
	});
}`;

if (content.includes(oldProcessRecording)) {
	content = content.replace(oldProcessRecording, newProcessRecording);
	fs.writeFileSync(chatPath, content, 'utf-8');
	console.log('[OK] 已添加语音识别功能');
} else {
	console.log('[FAIL] 未找到 processRecording 函数');
	console.log('可能代码格式已变化，需要手动修复');
}
