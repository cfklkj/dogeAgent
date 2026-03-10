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

// Python 桥接进程
function startPythonBridge() {
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, '..', 'desktop', 'bridge.py');
  
  pythonProcess = spawn(pythonPath, [scriptPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
    try {
      const lines = data.toString().split('\n');
      lines.forEach(line => {
        if (line.trim()) {
          const message = JSON.parse(line);
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('python-message', message);
          }
        }
      });
    } catch (e) {
      console.error('解析 Python 消息失败:', e);
    }
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Python 进程退出，代码：${code}`);
  });
  
  return pythonProcess;
}

// 发送消息到 Python
function sendToPython(message) {
  if (pythonProcess && pythonProcess.stdin.writable) {
    pythonProcess.stdin.write(JSON.stringify(message) + '\n');
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
    movable: true, // 启用移动
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
  
  startPythonBridge();
  createMainWindow();
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
  sendToPython(message);
});

ipcMain.on('open-chat', () => {
  createChatWindow();
});
