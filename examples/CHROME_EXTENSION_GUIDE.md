# Chrome 扩展基础：生命周期与核心 API

## 核心概念

Chrome 扩展由多个脚本组成，每个运行在不同的环境中，互相隔离：

```
┌──────────────────────────────────────────────────┐
│  Chrome 浏览器                                     │
│                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ background  │  │ content    │  │ popup      │  │
│  │ (后台常驻)  │  │ (注入网页) │  │ (点击图标) │  │
│  └────────────┘  └────────────┘  └────────────┘  │
│                                                    │
│  ┌────────────────────────────────────────────┐  │
│  │  网页 DOM (开发者工具里的那个页面)            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 四种脚本

### 1. Background Script (Service Worker)

**角色：** 扩展的大脑，后台运行，管理所有事件。

**生命周期（Manifest V3）：**

```
启动 → 空闲 (30s 无活动) → 休眠 → 事件触发 → 唤醒 → 空闲 → ...
```

MV3 的 Service Worker **不会一直运行**，30 秒无活动就会被 Chrome 杀掉。需要用 `chrome.alarms` 保活。

```javascript
// background.js

// 安装时触发（首次安装或更新）
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    console.log("首次安装");
  } else if (details.reason === "update") {
    console.log("更新到版本", details.previousVersion);
  }
});

// 浏览器启动时触发
chrome.runtime.onStartup.addListener(() => {
  console.log("浏览器启动");
});

// 消息监听（其他脚本发来的）
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  // msg: 发来的消息对象
  // sender: 发送者的信息（哪个 tab 发的）
  // sendResponse: 回调函数，返回结果

  if (msg.cmd === "ping") {
    sendResponse({ ok: true });
  }

  // 如果要异步返回，必须 return true
  return true;
});

// Alarms 保活（MV3 关键）
chrome.alarms.create("keepalive", { periodInMinutes: 0.4 }); // ~24s
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "keepalive") {
    // 做点什么保持 SW 存活
  }
});
```

### 2. Content Script

**角色：** 注入到网页中，能访问页面 DOM，但和页面的 JS 隔离。

**注入方式：**

```json
// manifest.json 中声明（自动注入）
"content_scripts": [{
  "matches": ["<all_urls>"],     // 匹配所有页面
  "js": ["content.js"],
  "run_at": "document_idle",     // 页面空闲时注入
  "all_frames": true             // iframe 里也注入
}]
```

```javascript
// 或者代码动态注入
chrome.scripting.executeScript({
  target: { tabId: 123 },
  files: ["content.js"]
});
```

**生命周期：** 跟随网页。页面关闭 → content script 销毁。

```javascript
// content.js

// 能访问页面 DOM
const title = document.title;

// 能和 background 通信
chrome.runtime.sendMessage({ cmd: "getData" }, (response) => {
  console.log("background 返回:", response);
});

// 能监听 background 发来的消息
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.cmd === "exec") {
    const result = document.querySelector(msg.selector)?.textContent;
    sendResponse({ data: result });
  }
});

// 注意：content script 和页面的 JS 是隔离的
// content.js 里的 window !== 页面的 window
// 页面里的全局变量，content.js 访问不到
```

**`world: "MAIN"` 注入：**

```json
// manifest.json
"content_scripts": [{
  "matches": ["<all_urls>"],
  "js": ["inject.js"],
  "world": "MAIN"      // 直接运行在页面 JS 环境中
}]
```

`world: "MAIN"` 下的脚本能访问页面的全局变量，但**不能用 Chrome API**（`chrome.runtime` 等）。

### 3. Popup Script

**角色：** 点击扩展图标弹出的 UI。

**生命周期：** 点击图标 → 打开 → 点击外部 → 关闭。**非常短命**，每次打开都是全新的。

```javascript
// popup.js
document.addEventListener("DOMContentLoaded", () => {
  // 获取当前 tab
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    console.log("当前页面:", tabs[0].url);
  });

  // 发消息给 background
  chrome.runtime.sendMessage({ cmd: "getCookies" }, (resp) => {
    console.log("收到:", resp);
  });
});
```

### 4. Options Page（可选）

**角色：** 扩展设置页面，右键扩展图标 → 选项。

```json
// manifest.json
"options_page": "options.html"
```

生命周期跟普通网页一样，打开就在，关了就没了。

## 通信方式

### 四种脚本之间的通信：

```
                sendMessage
popup ─────────────────────→ background
                                  │
                    sendMessage   │   sendMessage
content ←────────────────────────┘
                                  │
              scripting.executeScript / debugger
                                  │
                                  ▼
                              页面 DOM
```

```javascript
// ① popup/content → background（发消息）
chrome.runtime.sendMessage({ cmd: "ping" }, (response) => {
  // 收到回复
});

// ② background → content（指定 tab 发消息）
chrome.tabs.sendMessage(tabId, { cmd: "exec", code: "..." }, (response) => {
  // 收到回复
});

// ③ background → 页面（执行脚本）
chrome.scripting.executeScript({
  target: { tabId: tabId },
  func: () => document.title,    // 直接传函数
}, (results) => {
  console.log(results[0].result); // "Example Domain"
});

// ④ background → 页面（CDP 协议，不受 CSP 限制）
await chrome.debugger.attach({ tabId }, "1.3");
const result = await chrome.debugger.sendCommand(
  { tabId }, "Runtime.evaluate",
  { expression: "document.title", returnByValue: true }
);
await chrome.debugger.detach({ tabId });
```

## 核心权限（manifest.json）

```json
{
  "permissions": [
    "cookies",            // 读写 Cookie
    "tabs",               // 获取 tab 信息
    "activeTab",          // 当前 tab 权限（点击扩展时授予）
    "debugger",           // CDP 协议（强大的页面控制）
    "scripting",          // 动态注入脚本
    "alarms",             // 定时器（MV3 保活必备）
    "declarativeNetRequest", // 修改网络请求（如删 CSP 头）
    "management",         // 管理其他扩展
    "contentSettings"     // 修改内容设置（如自动下载）
  ],
  "host_permissions": [
    "<all_urls>"          // 所有网站的访问权限
  ]
}
```

## 关键 Chrome API

| API | 用途 | 示例 |
|-----|------|------|
| `chrome.tabs` | 管理 tab | `query()`, `create()`, `update()` |
| `chrome.cookies` | 读写 Cookie | `getAll()`, `set()`, `remove()` |
| `chrome.runtime` | 消息通信 | `sendMessage()`, `onMessage` |
| `chrome.scripting` | 注入脚本 | `executeScript()`, `insertCSS()` |
| `chrome.debugger` | CDP 协议 | `attach()`, `sendCommand()`, `detach()` |
| `chrome.alarms` | 定时器 | `create()`, `onAlarm` |
| `chrome.storage` | 持久存储 | `local.set()`, `local.get()` |
| `chrome.declarativeNetRequest` | 修改请求/响应 | 删 CSP 头、改 User-Agent |

## manifest.json 详解

manifest.json 是 Chrome 扩展的入口配置文件，Chrome 靠它知道你的扩展是什么、要什么权限、包含哪些脚本。

### 基础信息

```json
{
  "manifest_version": 3,          // MV3 是最新版，MV2 已废弃
  "name": "CDP Browse Bridge",    // 扩展名（显示在 chrome://extensions/ 中）
  "version": "1.0.0",             // 版本号，更新时必须改这个
  "description": "CDP-Bridge extension for cdp-browse"  // 一句话描述
}
```

### 权限声明

```json
{
  // 声明需要的 Chrome API 权限（安装时提示用户）
  "permissions": [
    "cookies",               // 读写任意网站的 Cookie
    "tabs",                  // 获取 tab 列表、URL、标题等
    "activeTab",             // 当前激活 tab 的临时权限（用户点击扩展图标时授予）
    "debugger",              // Chrome DevTools 协议（最强大：可以执行任意 JS、绕过 CSP）
    "scripting",             // 动态注入 JS/CSS 到页面
    "alarms",                // 定时器（MV3 Service Worker 保活必备）
    "declarativeNetRequest", // 拦截/修改网络请求（本项目用来删 CSP 头）
    "management",            // 管理其他扩展（启用/禁用/重载）
    "contentSettings"        // 修改内容设置（如允许自动下载）
  ],

  // 声明要访问哪些网站（<all_urls> = 所有网站）
  "host_permissions": ["<all_urls>"]
}
```

**permissions vs host_permissions 的区别：**

| | permissions | host_permissions |
|---|---|---|
| 控制什么 | 能用哪些 Chrome API | 能访问哪些网站 |
| 示例 | "cookies" = 能调 chrome.cookies API | "<all_urls>" = 所有网站都能操作 |
| 用户提示 | 安装时一次性授权 | 安装时提示"可以访问所有网站" |

### 后台脚本

```json
{
  "background": {
    "service_worker": "background.js"   // MV3 只能用 Service Worker（不能是持久页面）
  }
}
```

MV2 时的 `"persistent": true` 已废弃。MV3 的 Service Worker 空闲 30s 会被杀掉。

### 图标

```json
{
  "icons": {
    "16": "icons/icon-16.png",    // chrome://extensions/ 列表中的小图标
    "32": "icons/icon-32.png",    // Windows 任务栏
    "48": "icons/icon-48.png",    // chrome://extensions/ 管理页
    "128": "icons/icon-128.png"   // Chrome 网上应用店 + 安装对话框
  }
}
```

Chrome 会根据场景自动选择合适尺寸，所以一般准备这四个就够了。

### 内容脚本注入

```json
{
  "content_scripts": [
    {
      "matches": ["<all_urls>"],        // 匹配规则：注入到哪些页面
      "js": ["disable_dialogs.js"],     // 注入的 JS 文件
      "run_at": "document_start",       // 什么时候注入
      "all_frames": true,               // iframe 里也注入
      "world": "MAIN"                   // 运行在页面的 JS 环境中
    },
    {
      "matches": ["<all_urls>"],
      "js": ["config.js", "content.js"],
      "run_at": "document_idle",        // 页面加载完后注入
      "all_frames": true
      // 没有 world 字段 = 默认隔离世界
    }
  ]
}
```

**`run_at` 三个选项：**

| 值 | 时机 | 用途 |
|---|---|---|
| `"document_start"` | CSS 注入后，DOM 构建前 | 最早介入，覆盖页面默认行为（如拦截 alert） |
| `"document_end"` | DOM 构建完成，但图片等子资源未加载 | 需要操作 DOM 但不等图片 |
| `"document_idle"` | 页面完全加载（默认值） | 最安全，不会拖慢页面加载 |

**`matches` 匹配语法：**

```json
"<all_urls>"                    // 所有 http/https 页面
"*://*.example.com/*"           // example.com 及其子域名
"https://github.com/*"          // 只匹配 github.com
"http://localhost:*/*"          // 本地开发服务器
```

### 扩展图标与弹窗

```json
{
  "action": {
    "default_icon": {                   // 工具栏上的图标
      "16": "icons/icon-16.png",
      "32": "icons/icon-32.png",
      "48": "icons/icon-48.png",
      "128": "icons/icon-128.png"
    },
    "default_popup": "popup.html",      // 点击图标弹出的页面
    "default_title": "CDP Browse Bridge" // 鼠标悬停时的提示文字
  }
}
```

**`icons` vs `action.default_icon` 的区别：**

| | icons | action.default_icon |
|---|---|---|
| 显示位置 | chrome://extensions/ 管理页 | 浏览器工具栏（右上角） |
| 用途 | 管理界面中的标识 | 用户日常看到的图标 |

### 其他常用字段（本项目未用到）

```json
{
  "options_page": "options.html",              // 右键图标 → 选项页
  "devtools_page": "devtools.html",            // DevTools 面板
  "web_accessible_resources": [{               // 允许网页访问扩展内的资源
    "resources": ["images/*.png"],
    "matches": ["<all_urls>"]
  }],
  "content_security_policy": {                 // 扩展自身的 CSP
    "extension_pages": "script-src 'self'; object-src 'self'"
  },
  "background": {
    "service_worker": "bg.js",
    "type": "module"                           // 支持 ES Module import
  }
}
```

## CSP（Content Security Policy）

CSP 是网站通过 HTTP 响应头设置的**安全策略**，控制页面能执行什么：

```http
Content-Security-Policy: script-src 'self'; style-src 'self'
```

意思是：只允许加载同域的 JS/CSS，禁止内联脚本、禁止 `eval()`。

### 为什么扩展要删掉 CSP

扩展要在别人页面里执行 JS（`eval`、`new Function()`），CSP 会直接拦截：

```
CSP 头: script-src 'self'
     │
     ▼
扩展尝试 eval("document.title")
     │
     ▼
浏览器: Refused to evaluate a string as JavaScript because 'unsafe-eval' is not allowed
```

### 本项目的双重 CSP 清除

**① background.js — 删除 HTTP 响应头中的 CSP：**

```javascript
chrome.declarativeNetRequest.updateDynamicRules({
  addRules: [{
    action: {
      type: "modifyHeaders",
      responseHeaders: [
        { header: "content-security-policy", operation: "remove" }
      ]
    },
    condition: { urlFilter: "*", resourceTypes: ["main_frame", "sub_frame"] }
  }]
});
```

**② disable_dialogs.js — 删除 HTML meta 标签中的 CSP：**

```javascript
document.querySelectorAll('meta[http-equiv="Content-Security-Policy"]')
  .forEach((e) => e.remove());
```

两种形式的 CSP 都干掉，确保扩展能在任何页面执行 JS。

### CSP 的 JS 执行 fallback 链

即使删了 CSP，有时 `chrome.scripting.executeScript` 还是会失败（某些页面环境问题），所以 background.js 有两层 fallback：

```
① chrome.scripting.executeScript  （优先，轻量）
        │ 失败？
        ▼
② chrome.debugger + Runtime.evaluate  （fallback，CDP 协议，不受任何限制）
```

## 反爬虫检测分析

### 为什么比 Puppeteer/Playwright 更隐蔽

| 检测方式 | Puppeteer/Playwright | CDP Browse 扩展 |
|---------|---------------------|----------------|
| `navigator.webdriver` | `true` ← 必定暴露 | `undefined` ← 真实浏览器值 |
| 调试端口 | `localhost:9222` 开着 | 没有调试端口暴露给页面 |
| 浏览器指纹 | headless 特征明显（无 GPU、无字体） | 完整的真实用户环境 |
| Cookie/登录态 | 需要手动搬运 | 复用用户真实登录态 |
| JS 执行环境 | 隔离的新浏览器实例 | 真实浏览器，有用户历史数据 |

Puppeteer/Playwright 启动的是一个**全新的浏览器实例**，几乎所有反爬系统都能识别。CDP Browse 扩展控制的是**用户正在使用的真实浏览器**，从根本上避免了这些特征。

### 不完全不可检测

虽然比 Puppeteer 隐蔽得多，但仍有可能被发现：

```javascript
// ① 扩展注入了可见的 DOM 元素
document.getElementById("ljq-ind")  // 右下角 "CDP Browse 已连接" 徽章

// ② disable_dialogs.js 覆盖了原生函数，toString 会暴露
window.alert.toString()
// 正常: "function alert() { [native code] }"
// 被覆盖后: "function () { toast("alert", msg); }"

// ③ CSP 安全头被删除了
// 服务器设置的 Content-Security-Policy 头不见了

// ④ debugger 会短暂显示提示条
// Chrome 顶部出现 "扩展正在调试此浏览器" 黄色提示栏

// ⑤ 扩展资源探测
// 网站可以尝试加载 chrome-extension://扩展ID/资源 来探测扩展是否存在
```

### 总结

| 安全等级 | 场景 | 能否应对 |
|---------|------|---------|
| 低（大多数网站） | 只检查 navigator.webdriver | 轻松绕过 |
| 中（电商平台等） | 检查浏览器指纹 + 行为分析 | 基本够用 |
| 高（银行、票务） | 多维度检测 + 扩展探测 | 可能被发现 |

核心优势：**用真实浏览器 + 真实登录态**，避开了自动化工具最大的暴露点（webdriver 标志和 headless 特征）。

## 网站如何检测扩展（防御视角）

写死 DOM 元素 ID 的方式不可靠（改个 ID 就绕过了），可靠的做法是**模式检测 + 服务端判断**。

### 服务端检测（最可靠）

**① CSP 报告差异**

```
正常用户: 服务端设 CSP → 浏览器执行 → 偶尔有违规报告 → 正常
扩展用户: 扩展删 CSP → 浏览器不执行 → 零报告 → 异常
```

设了 `report-uri` 的 CSP，如果一个活跃用户从未产生过报告，反而可疑。

**② CSP 陷阱（配合前端埋点）**

```html
<!-- 服务端 CSP: script-src 'self' -->
<!-- 这个内联脚本只有 CSP 被删除后才会执行 -->
<script>window.__inlineExecuted = true</script>

<script>
  // 外部脚本，CSP 允许
  if (window.__inlineExecuted) {
    navigator.sendBeacon('/security', JSON.stringify({ csp: 'bypassed' }));
  }
</script>
```

**③ Header 完整性校验**

浏览器请求的 header 序列是固定的，扩展注入的请求可能缺少某些 header（如 Referer、Sec-Fetch-* 等）。对比正常用户的 header 指纹。

**④ 行为时序分析**

```
真人:   页面加载 → 阅读 3-10s → 滚动 → 点击
自动化: 页面加载 → 立刻执行 JS → 连续操作无间隔
```

用请求时间戳的方差就能区分。

### 前端通用检测（不写死任何 ID）

**① 原生函数完整性 — 最难绕过**

```javascript
function isNative(fn) {
  return /\[native code\]/.test(fn.toString())
      && /\[native code\]/.test(fn.call.toString());
}

['alert', 'confirm', 'prompt'].forEach(fn => {
  if (!isNative(window[fn])) {
    // 覆盖 toString 本身也是一种暴露
    report({ type: 'native_override', fn });
  }
});
```

不管扩展怎么改 ID，覆盖 alert/confirm 就会暴露。

**② 通用 MutationObserver — 检测模式不是 ID**

```javascript
let suspiciousMutations = 0;

new MutationObserver((muts) => {
  for (const m of muts) {
    for (const node of m.addedNodes) {
      if (node.nodeType !== 1) continue;

      // 页面自己不会插入 display:none 的空 div
      if (node.tagName === 'DIV'
          && !node.textContent.trim()
          && node.style.display === 'none') {
        suspiciousMutations++;
      }

      // z-index:2147483647 是最大值，正常业务不会用
      if (node.tagName === 'STYLE'
          && node.textContent.includes('2147483647')) {
        suspiciousMutations++;
      }
    }
  }
}).observe(document.documentElement, { childList: true, subtree: true });
```

### 核心原则

**不要在前端抓特征，让服务端看行为。** 前端只做一件事 — 把观察到的异常模式静默上报（`navigator.sendBeacon`），判断交给后端。前端拦截只会让对抗升级，服务端根据上报数据决定限流、弹验证码或封号。

## 本项目用到的关键技术

| 技术 | 文件 | 目的 |
|------|------|------|
| `chrome.debugger` (CDP) | background.js | 绕过 CSP 执行 JS |
| `chrome.scripting.executeScript` | background.js | 在页面执行 JS（优先方式） |
| `WebSocket` 客户端 | background.js | 连接 cdp-bridge MCP 服务 |
| `chrome.alarms` | background.js | MV3 Service Worker 保活 |
| `declarativeNetRequest` | background.js | 删除 CSP 响应头 |
| `world: "MAIN"` | disable_dialogs.js | 直接拦截页面的 alert/confirm/prompt |
| DOM 注入 + MutationObserver | content.js | 用隐藏 DOM 元素传递指令 |
