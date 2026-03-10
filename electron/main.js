/**
 * dogeAgent - Electron 主进程
 */
const { app, BrowserWindow, Tray, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow = null;
let chatWindow = null;
let tray = null;
let pythonProcess = null;
let pythonReady = false;

// Python 桥接进程
function startPythonBridge() {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, '..', 'desktop', 'bridge.py');
  
  console.log('Starting Python bridge:', scriptPath);
  
  pythonProcess = spawn(pythonPath, [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: path.join(__dirname, '..'),
    env: {
      ...process.env,
      PYTHONIOENCODING: 'utf-8'  // 强制 Python 使用 UTF-8
    }
  });

  // 处理 Python 输出
  pythonProcess.stdout.on('data', (data) => {
    // 关键修复：使用 Buffer 的 toString('utf8') 确保 UTF-8 解码
    const str = data.toString('utf8');
    console.log(`Python: ${str}`);
    
    try {
      const lines = str.split('\n');
      lines.forEach(line => {
        if (line.trim()) {
          const message = JSON.parse(line);
          console.log('Python message:', message);
          
          // 检查是否是 ready 消息
          if (message.type === 'ready') {
            pythonReady = true;
            console.log('Python bridge ready');
            
            // 自动发送初始化消息
            setTimeout(() => {
              sendToPython({ type: 'init', payload: {} });
            }, 500);
            
            // 通知所有窗口
            if (chatWindow && !chatWindow.isDestroyed()) {
              chatWindow.webContents.send('connection-status', 'connected');
            }
            if (mainWindow && !mainWindow.isDestroyed()) {
              mainWindow.webContents.send('connection-status', 'connected');
            }
          }
          
          // 转发到聊天窗口
          if (chatWindow && !chatWindow.isDestroyed()) {
            chatWindow.webContents.send('python-message', message);
          }
          
          // 也转发到主窗口（用于状态显示）
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('python-message', message);
          }
        }
      });
    } catch (e) {
      console.error('解析 Python 消息失败:', e, str);
    }
  });

  // 处理 Python 错误输出
  pythonProcess.stderr.on('data', (data) => {
    const str = data.toString('utf8');
    console.error(`Python Error: ${str}`);
  });

  // 处理 Python 进程退出
  pythonProcess.on('close', (code) => {
    console.log(`Python 进程退出，代码：${code}`);
    pythonReady = false;
    
    // 通知窗口连接已断开
    if (chatWindow && !chatWindow.isDestroyed()) {
      chatWindow.webContents.send('connection-status', 'disconnected');
    }
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('connection-status', 'disconnected');
    }
  });

  // 处理 Python 进程错误
  pythonProcess.on('error', (err) => {
    console.error('Python 进程启动失败:', err);
    pythonReady = false;
    
    if (chatWindow && !chatWindow.isDestroyed()) {
      chatWindow.webContents.send('connection-status', 'disconnected');
    }
  });

  return pythonProcess;
}

// 发送消息到 Python
function sendToPython(message) {
  if (!pythonProcess) {
    console.log('Python process not started');
    return false;
  }
  
  try:
    // 使用 JSON.stringify 确保正确的 JSON 格式
    const jsonStr = JSON.stringify(message);
    console.log('Sending to Python:', jsonStr);
    pythonProcess.stdin.write(jsonStr + '\n');
    return true;
  } catch (e) {
    console.error('发送到 Python 失败:', e);
    return false;
  }
}

// 创建主窗口（宠物窗口）
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 400,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    hasShadow: false,
    resizable: false,
    movable: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  
  mainWindow.loadFile(path.join(__dirname, 'pet.html'));
  mainWindow.setAlwaysOnTop(true, 'screen-saver');
  
  // 监听打开聊天窗口的请求
  ipcMain.on('open-chat', () => {
    console.log('open-chat 请求收到');
    createChatWindow();
  });
  
  mainWindow.on('double-click', () => {
    console.log('主窗口双击事件');
    if (!chatWindow || chatWindow.isDestroyed()) {
      createChatWindow();
    } else {
      chatWindow.focus();
    }
  });
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 创建聊天窗口
function createChatWindow() {
  if (chatWindow && !chatWindow.isDestroyed()) {
    console.log('聊天窗口已存在，聚焦');
    chatWindow.focus();
    return;
  }
  
  console.log('创建新的聊天窗口');
  chatWindow = new BrowserWindow({
    width: 500,
    height: 600,
    frame: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  
  chatWindow.loadFile(path.join(__dirname, 'chat.html'));
  chatWindow.setTitle('dogeAgent - 聊天');
  
  // 监听聊天窗口的发送请求
  chatWindow.webContents.on('did-finish-load', () => {
    console.log('Chat window loaded, Python ready:', pythonReady);
    if (pythonReady) {
      chatWindow.webContents.send('connection-status', 'connected');
    } else {
      chatWindow.webContents.send('connection-status', 'connecting');
    }
  });
  
  chatWindow.on('closed', () => {
    console.log('聊天窗口已关闭');
    chatWindow = null;
  });
}

// 监听发送消息到 Python 的请求
ipcMain.on('send-to-python', (event, message) => {
  console.log('收到 send-to-python 请求:', message);
  sendToPython(message);
});

// 创建系统托盘
function createTray() {
  const iconPath = path.join(__dirname, '..', 'assets', 'icons', 'icon.png');
  tray = new Tray(iconPath || path.join(__dirname, 'icon.png'));
  
  const contextMenu = Menu.buildFromTemplate([
    { label: '打开聊天', click: () => createChatWindow() },
    { label: '显示宠物', click: () => mainWindow && mainWindow.show() },
    { label: '隐藏宠物', click: () => mainWindow && mainWindow.hide() },
    { type: 'separator' },
    { label: '退出', click: () => app.quit() }
  ]);
  
  tray.setToolTip('dogeAgent - 智能桌面宠物');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
    }
  });
}

// 创建窗口
app.whenReady().then(() => {
  createTray();
  createMainWindow();
  startPythonBridge();
});

// 窗口全部关闭时
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 清理资源
app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

// 导出给渲染进程使用
module.exports = { sendToPython };
