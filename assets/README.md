# Assets 资源文件

本目录存放 dogeAgent 的所有资源文件。

## 目录结构

```
assets/
├── icons/          # 图标文件
│   ├── icon.png    # 应用图标
│   └── doge.png    # 柴犬主图
├── animations/     # 动画资源
│   └── idle.gif    # 待机动画
└── sounds/         # 声音资源
    └── tts_cache/  # TTS 缓存
```

## 需要准备的资源

### 图标文件
- `icon.png`: 256x256 像素，应用图标
- `doge.png`: 300x300 像素，透明背景柴犬图片

### 动画资源
- `idle.gif`: 待机动画（可选）
- `happy.gif`: 开心动画（可选）
- `thinking.gif`: 思考动画（可选）

## 资源获取

可以从以下网站获取免费资源：
- 图标：https://www.iconfinder.com/
- 柴犬图片：https://www.freepik.com/
- 动画：使用 CSS 动画替代或自行制作

## 临时方案

如果暂时没有资源文件，可以使用：
- 纯色背景 + CSS 动画
- 使用 emoji 作为临时图标
- 从开源项目借用资源（注意版权）
