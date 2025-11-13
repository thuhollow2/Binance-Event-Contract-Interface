#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android 15优化的币安App控制器
解决权限问题和Hidden API策略错误
"""

import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OptimizedAppiumController:
    def __init__(self, device_name="40f06c22", appium_server="http://localhost:4723"):
        """
        优化的Appium控制器，专为Android 15设计
        """
        self.device_name = device_name
        self.appium_server = appium_server
        self.driver = None
        self.wait = None
        
    def connect_device(self):
        """连接设备并启动币安App - Android 15优化版本"""
        print("正在连接设备...")
        print(f"设备ID: {self.device_name}")
        print("注意: 使用Android 15优化配置")
        
        # Android 15专用配置
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = self.device_name
        options.app_package = "com.binance.dev"
        options.app_activity = "com.binance.activity.MainActivity"
        options.automation_name = "UiAutomator2"
        
        # 基本设置
        options.no_reset = True
        options.new_command_timeout = 300
        
        # Android 15权限问题解决方案
        options.ignore_hidden_api_policy_error = True
        options.skip_device_initialization = True
        options.skip_server_installation = True
        
        # 额外的兼容性设置
        options.use_keystore = False
        options.skip_unlock = True
        options.disable_android_watchers = True
        
        try:
            print("正在建立连接...")
            self.driver = webdriver.Remote(self.appium_server, options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("✓ 设备连接成功")
            print("✓ 币安App启动中...")
            
            # 等待应用启动
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            print("\n可能的解决方案:")
            print("1. 确保Appium服务器正在运行")
            print("2. 确保币安App已安装")
            print("3. 如果是权限问题，请尝试重启手机")
            return False
    
    def tap(self, x, y):
        """点击屏幕坐标"""
        try:
            self.driver.tap([(x, y)])
            print(f"✓ 点击坐标: ({x}, {y})")
            return True
        except Exception as e:
            print(f"✗ 点击失败: {e}")
            return False
    
    def swipe(self, start_x, start_y, end_x, end_y, duration=1000):
        """滑动屏幕"""
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            print(f"✓ 滑动: ({start_x},{start_y}) -> ({end_x},{end_y})")
            return True
        except Exception as e:
            print(f"✗ 滑动失败: {e}")
            return False
    
    def screenshot(self, filename="screenshot.png"):
        """截屏"""
        try:
            self.driver.save_screenshot(filename)
            print(f"✓ 截屏保存: {filename}")
            return True
        except Exception as e:
            print(f"✗ 截屏失败: {e}")
            return False
    
    def wait_seconds(self, seconds):
        """等待指定秒数"""
        print(f"等待 {seconds} 秒...")
        time.sleep(seconds)
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        try:
            size = self.driver.get_window_size()
            print(f"屏幕尺寸: {size['width']} x {size['height']}")
            return size
        except Exception as e:
            print(f"✗ 获取屏幕尺寸失败: {e}")
            return None
    
    def click_by_text(self, text):
        """通过文本点击元素"""
        try:
            element = self.driver.find_element(AppiumBy.XPATH, f"//*[contains(@text, '{text}')]")
            element.click()
            print(f"✓ 点击文本: {text}")
            return True
        except Exception as e:
            print(f"✗ 未找到文本: {text}")
            return False
    
    def input_text_by_class(self, text, class_name="android.widget.EditText"):
        """在输入框中输入文本"""
        try:
            elements = self.driver.find_elements(AppiumBy.CLASS_NAME, class_name)
            if elements:
                elements[0].clear()
                elements[0].send_keys(text)
                print(f"✓ 输入文本: {text}")
                return True
            else:
                print(f"✗ 未找到输入框")
                return False
        except Exception as e:
            print(f"✗ 输入失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        try:
            if self.driver:
                self.driver.quit()
                print("✓ 连接已关闭")
        except Exception as e:
            print(f"关闭连接时出错: {e}")

def main():
    """主函数 - Android 15优化版本"""
    print("=== Android 15优化币安控制器 ===")
    print("专为解决Android 15权限问题而设计")
    print()
    
    controller = OptimizedAppiumController()
    
    try:
        if not controller.connect_device():
            print("连接失败，退出程序")
            return
        
        print("\n✓ 连接成功！现在可以控制手机了")
        
        # 获取屏幕信息
        screen_size = controller.get_screen_size()
        
        # 截屏
        controller.screenshot("binance_start.png")
        
        print("\n=== 可用命令 ===")
        print("tap(x, y) - 点击坐标")
        print("swipe(x1, y1, x2, y2) - 滑动")  
        print("screenshot('name.png') - 截屏")
        print("click_by_text('文本') - 点击包含文本的元素")
        print("input_text_by_class('文本') - 输入文本")
        print("wait_seconds(秒数) - 等待")
        print("quit - 退出")
        print()
        
        # 交互模式
        while True:
            try:
                cmd = input("控制器 >>> ").strip()
                
                if cmd.lower() in ['quit', 'exit', 'q']:
                    break
                elif cmd.startswith('tap('):
                    # 解析tap命令
                    coords = cmd[4:-1].split(',')
                    if len(coords) == 2:
                        x, y = int(coords[0].strip()), int(coords[1].strip())
                        controller.tap(x, y)
                elif cmd.startswith('swipe('):
                    # 解析swipe命令
                    coords = cmd[6:-1].split(',')
                    if len(coords) == 4:
                        x1, y1, x2, y2 = [int(c.strip()) for c in coords]
                        controller.swipe(x1, y1, x2, y2)
                elif cmd.startswith('screenshot('):
                    # 解析screenshot命令
                    filename = cmd[11:-1].strip().strip('"\'')
                    controller.screenshot(filename)
                elif cmd.startswith('click_by_text('):
                    # 解析click_by_text命令
                    text = cmd[15:-1].strip().strip('"\'')
                    controller.click_by_text(text)
                elif cmd.startswith('input_text_by_class('):
                    # 解析input_text_by_class命令
                    text = cmd[20:-1].strip().strip('"\'')
                    controller.input_text_by_class(text)
                elif cmd.startswith('wait_seconds('):
                    # 解析wait_seconds命令
                    seconds = int(cmd[13:-1].strip())
                    controller.wait_seconds(seconds)
                elif cmd == 'help':
                    print("可用命令:")
                    print("tap(500, 1000)")
                    print("swipe(500, 1500, 500, 500)")
                    print("screenshot('test.png')")
                    print("click_by_text('登录')")
                    print("input_text_by_class('test@example.com')")
                    print("wait_seconds(3)")
                elif cmd:
                    print("未知命令，输入 'help' 查看帮助")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"命令执行错误: {e}")
        
    except Exception as e:
        print(f"程序运行错误: {e}")
    finally:
        controller.close()

if __name__ == "__main__":
    main()