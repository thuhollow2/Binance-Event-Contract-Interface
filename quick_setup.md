# 快速设置指南

## 1. 安装 Node.js 和 Appium

如果你还没有安装，请按以下步骤操作：

### 安装 Node.js

1. 从 https://nodejs.org 下载并安装 Node.js
2. 验证安装: `node --version`

### 安装 Appium

```bash
npm install -g appium
appium driver install uiautomator2
```

## 2. 准备手机

### Android 手机设置:

1. 进入设置 -> 关于手机
2. 连续点击"版本号"7 次开启开发者选项
3. 进入设置 -> 开发者选项
4. 开启"USB 调试"
5. 用 USB 线连接电脑
6. 手机上确认调试授权

## 3. 运行

### 启动 Appium 服务器

```bash
appium
```

保持这个终端窗口打开

### 运行控制器

在新的终端窗口中:

```bash
python appium_controller.py
```

## 4. 获取设备 ID

如果你有 adb 工具，可以通过以下命令查看设备 ID:

```bash
adb devices
```

如果没有 adb，通常设备 ID 格式为:

- 模拟器: `emulator-5554`
- 真机: 类似 `abc123def456` 的字符串

## 故障排除

**如果连接失败:**

1. 确保 Appium 服务器在运行 (http://localhost:4723 应该可以访问)
2. 确保手机已连接并允许 USB 调试
3. 确保币安 App 已安装在手机上

**常见错误:**

- "Appium 服务器未启动" -> 运行 `appium` 命令
- "设备未连接" -> 检查 USB 连接和调试权限
- "应用未找到" -> 确保币安 App 已安装
