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
    cwd: path.join(__dirname, '..')
  });
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
    try {
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        if (line.trim()) {
          const message = JSON.parse(line);
          console.log('Python message:', message);
          
          // 检查是否是 ready 消息
          if (message.type === 'ready') {
            pythonReady = true;
            console.log('Python bridge ready');
            
            // 通知所有窗口
            if (chatWindow && !chatWindow.isDestroyed()) {
              chatWindow.webContents.send('connection-status', 'connected');
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
      console.error('解析 Python 消息失败:', e, data.toString());
    }
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });
  
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
  if (!pythonProcess || !pythonReady) {
    console.log('Python not ready, queueing message:', message);
    return false;
  }
  
  try {
    pythonProcess.stdin.write(JSON.stringify(message) + '\n');
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
  
  mainWindow.on('double-click', () => {
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
    chatWindow.focus();
    return;
  }
  
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
  
  // 聊天窗口准备好后，发送连接状态
  chatWindow.webContents.on('did-finish-load', () => {
    console.log('Chat window loaded, Python ready:', pythonReady);
    if (pythonReady) {
      chatWindow.webContents.send('connection-status', 'connected');
    } else {
      chatWindow.webContents.send('connection-status', 'connecting');
    }
  });
  
  chatWindow.on('closed', () => {
    chatWindow = null;
  });
}

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
  
  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    }
  });
}

// 应用就绪
app.whenReady().then(() => {
  console.log('dogeAgent 启动中...');
  
  // 启动 Python 桥接
  startPythonBridge();
  
  // 创建窗口
  createMainWindow();
  
  // 延迟创建托盘
  setTimeout(createTray, 1000);
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

// IPC 通信
ipcMain.on('send-to-python', (event, message) => {
  console.log('IPC send-to-python:', message);
  sendToPython(message);
});

ipcMain.on('open-chat', () => {
  createChatWindow();
});

ipcMain.on('get-python-status', (event) => {
  event.reply('python-status', { ready: pythonReady });
});
