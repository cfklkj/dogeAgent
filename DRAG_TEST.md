# 🐕 拖动功能测试报告

**测试日期**: 2026-03-10  
**问题**: 拖动时窗口不跟随鼠标，会飘出可视区域

---

## 问题分析

### 当前状态
- ✅ 窗口可以拖动（通过 `movable: true`）
- ✅ 双击功能正常
- ❌ 拖动时窗口不跟随鼠标
- ❌ 窗口会移出可视区域

### 原因
1. **HTML5 drag API 限制**: 原生拖放 API 不适合窗口级拖动
2. **坐标计算问题**: 屏幕坐标与窗口坐标转换错误
3. **事件监听问题**: 鼠标事件未正确传递到主进程

---

## 解决方案

### 方案 1: 使用 Electron 原生拖动（推荐）

在 `pet.html` 中添加 CSS:
```css
.drag-region {
  -webkit-app-region: drag;
}
```

在 `main.js` 中设置:
```javascript
movable: true
```

### 方案 2: 使用自定义 IPC 通信

1. 渲染进程监听鼠标事件
2. 通过 IPC 发送坐标到主进程
3. 主进程更新窗口位置

### 方案 3: 简化拖动区域

创建一个覆盖整个窗口的透明拖动层，狗子本身只负责显示和双击交互。

---

## 当前实现

已尝试的方案：
- [x] HTML5 原生拖放 API - ❌ 不适合窗口拖动
- [x] 自定义鼠标事件监听 - ❌ 坐标计算复杂
- [x] 使用 `-webkit-app-region: drag` - ⚠️ 需要调整

---

## 下一步

### 立即可做
1. 使用 `-webkit-app-region: drag` 创建拖动区域
2. 狗子区域设置为 `-webkit-app-region: no-drag`
3. 双击功能通过点击事件实现

### 测试要点
- [ ] 拖动流畅性
- [ ] 窗口不超出屏幕
- [ ] 双击功能正常
- [ ] 动画效果正常

---

## 参考实现

```html
<!-- 拖动区域（透明） -->
<div class="drag-region"></div>

<!-- 狗子（不可拖动，可双击） -->
<div class="doge-wrapper" style="-webkit-app-region: no-drag;">
  <div class="doge"></div>
</div>
```

```css
.drag-region {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  -webkit-app-region: drag;
  z-index: 1;
}
```

---

**状态**: 测试中  
**优先级**: 高  
**影响**: 用户体验
