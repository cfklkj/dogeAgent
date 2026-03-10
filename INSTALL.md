# 🐶 dogeAgent 安装指南

## 系统要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

## 安装步骤

### 1. 克隆/下载项目

```bash
cd H:\openclawWk\workspace-magic\workspace\2026\03\10\dogeAgent
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

如果遇到 `pyaudio` 安装问题：
- **Windows**: 下载预编译包：https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- **Mac**: `brew install portaudio`
- **Linux**: `sudo apt-get install python3-pyaudio`

### 3. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的 NVIDIA API Key
# 获取 API Key: https://build.nvidia.com/
```

### 4. 安装 Node.js 依赖

```bash
npm install
```

### 5. 启动应用

**方式一：使用启动脚本（推荐）**
```bash
python start.py
```

**方式二：手动启动**
```bash
# 确保 Python 依赖已安装
# 启动 Electron
npm start
```

## 常见问题

### Q: NVIDIA API Key 在哪里获取？
A: 访问 https://build.nvidia.com/ 注册并获取免费 API Key

### Q: 启动后看不到宠物窗口？
A: 检查系统托盘，dogeAgent 的图标应该在那里

### Q: 如何切换模型？
A: 在聊天窗口中发送 `/model google` 或 `/model nvidia`

## 开发模式

```bash
# 热重载模式
npm run dev

# 构建可执行文件
npm run build
```

## 卸载

直接删除项目目录即可，数据存储在：
- Windows: `%APPDATA%/dogeAgent`
- Mac/Linux: `~/.local/share/dogeAgent`
