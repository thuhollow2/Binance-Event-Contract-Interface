# Appium 手机控制器使用说明

## 环境准备

1. **安装 Python 依赖**

```bash
pip install -r requirements.txt
```

2. **安装 Appium**

```bash
npm install -g appium
appium driver install uiautomator2
```

3. **连接手机**

- 开启开发者选项
- 启用 USB 调试
- 连接电脑
- 确认调试授权

4. **验证连接**

```bash
adb devices
```

## 使用方法

### 1. 启动 Appium 服务器

```bash
appium
```

### 2. 运行控制器

```bash
python appium_controller.py
```

### 3. 基本操作

```python
from appium_controller import SimpleAppiumController

# 创建控制器
controller = SimpleAppiumController()

# 连接设备
controller.connect_device()

# 点击元素 (通过ID)
controller.click_element("id", "com.binance.dev:id/button_login")

# 点击元素 (通过XPath)
controller.click_element("xpath", "//android.widget.Button[@text='登录']")

# 输入文本
controller.input_text("id", "com.binance.dev:id/edit_email", "your_email@example.com")

# 点击坐标
controller.tap(500, 1000)

# 滑动屏幕
controller.swipe(500, 1500, 500, 500)  # 向上滑动

# 等待
controller.sleep(2)

# 截屏
controller.take_screenshot("current_screen.png")

# 断开连接
controller.close()
```

## 查找元素

使用 **Appium Inspector** 来查找元素的 ID 和 XPath：

1. 启动 Appium 服务器
2. 打开 Appium Inspector (http://localhost:4723)
3. 配置连接参数后点击连接
4. 在界面中点击元素查看其属性

## 注意事项

- 确保 Appium 服务器已启动 (http://localhost:4723)
- 确保手机已连接并开启 USB 调试
- 币安 App 包名: `com.binance.dev`
- 如果连接失败，检查设备 ID 是否正确
