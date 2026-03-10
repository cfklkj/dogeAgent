# 🐶 dogeAgent 使用说明

**版本**: v3.0.0  
**更新日期**: 2026-03-10

---

## 🚀 启动方式

### 方式 1: 使用启动脚本
```bash
cd H:\openclawWk\workspace-magic\workspace\2026\03\10\dogeAgent
python start.py
```

### 方式 2: 直接启动
```bash
npm start
```

---

## 🎮 操作指南

### 窗口拖动
- **拖动区域**: 窗口顶部透明区域（狗子上方）
- **操作**: 鼠标左键按住拖动

### 交互操作
- **双击狗子**: 打开聊天窗口
- **右键托盘图标**: 显示菜单
  - 打开聊天
  - 显示/隐藏宠物
  - 退出应用

### 聊天窗口
- **输入文字**: 在底部输入框输入
- **发送消息**: 按 Enter 或点击发送按钮
- **关闭窗口**: 点击关闭按钮

---

## 🐕 功能特性

### 1. 桌面宠物
- 透明窗口显示
- 待机动画（上下浮动）
- 状态动画（说话、思考、开心等）

### 2. 智能对话
- 基于 NVIDIA z-ai/glm5 模型
- 支持多轮对话
- 情感系统响应

### 3. 工具系统
- 时间查询
- 日期查询
- 数学计算
- 天气查询

### 4. 情感系统
- 亲密度等级
- 情感状态机
- 个性化问候

---

## ⚙️ 配置说明

### 环境变量 (.env)
```bash
# NVIDIA API Key (必需)
NVIDIA_API_KEY=nvapi-xxxxx...

# Google API Key (可选)
GOOGLE_API_KEY=AIza...

# 默认模型提供商
DEFAULT_MODEL_PROVIDER=nvidia
```

### 获取 API Key
- NVIDIA: https://build.nvidia.com/
- Google: https://makersuite.google.com/app/apikey

---

## 🎨 自定义

### 更换狗子图片
1. 准备图片：`doge.png` (300x300 透明背景)
2. 放置到：`assets/icons/doge.png`
3. 重启应用

### 更换应用图标
1. 准备图标：`icon.png` (256x256)
2. 放置到：`assets/icons/icon.png`
3. 重启应用

### 修改动画
编辑 `electron/pet.html` 中的 CSS 动画部分

---

## 🐛 常见问题

### Q: 窗口无法拖动？
A: 确保鼠标在窗口顶部透明区域拖动，而不是狗子本身

### Q: 狗子图片不显示？
A: 检查 `assets/icons/doge.png` 是否存在，或使用默认图片

### Q: 对话无响应？
A: 检查 NVIDIA API Key 是否正确，网络是否畅通

### Q: 窗口关闭后无法恢复？
A: 点击系统托盘图标，选择"显示宠物"

### Q: 聊天窗口打不开？
A: 双击狗子身体任意位置，或右键托盘图标选择"打开聊天"

---

## 📝 快捷键

| 快捷键 | 功能 |
|--------|------|
| 双击狗子 | 打开聊天窗口 |
| 拖动窗口顶部 | 移动窗口位置 |
| 右键托盘 | 显示菜单 |
| Enter | 发送消息 |
| Esc | 关闭窗口 |

---

## 🔧 高级功能

### 命令行测试
```bash
# 核心功能测试
python run_test.py

# CLI 聊天模式
python cli_chat.py
```

### 开发者模式
```bash
# 查看日志
npm start --enable-logging

# 开发者工具
# 在聊天窗口按 F12 打开开发者工具
```

---

## 📊 项目结构

```
dogeAgent/
├── electron/           # Electron 前端
│   ├── main.js        # 主进程
│   ├── pet.html       # 宠物窗口
│   └── chat.html      # 聊天窗口
├── agent/             # Agent 核心
├── tools/             # 工具函数
├── storage/           # 数据存储
├── weather/           # 天气模块
├── search/            # 搜索模块
└── plugins/           # 插件系统
```

---

## 🎯 下一步

### 立即可用
- [x] 拖动窗口
- [x] 双击打开聊天
- [x] 与 AI 对话
- [x] 使用工具查询

### 待完善
- [ ] 添加更多动画状态
- [ ] 实现语音交互
- [ ] 添加插件支持
- [ ] 云同步功能

---

## 📞 支持

如遇问题，请检查：
1. `.env` 文件配置
2. 网络连接
3. 日志输出

**项目状态**: 核心功能可用  
**GUI 状态**: 正常运行  
**测试者**: Fly

---

**享受与 dogeAgent 的时光！** 🐶✨
