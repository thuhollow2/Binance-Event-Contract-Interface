#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Appium手机控制器
用于操作币安App
"""

import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SimpleAppiumController:
    def __init__(self, device_name=None, appium_server="http://localhost:4723"):
        """
        初始化Appium控制器
        
        Args:
            device_name: 设备名称，如果为None会尝试连接第一个可用设备
            appium_server: Appium服务器地址
        """
        self.device_name = device_name
        self.appium_server = appium_server
        self.driver = None
        self.wait = None
        
    def connect_device(self):
        """连接设备并启动币安App"""
        print("正在连接设备...")
        
        # 如果没有指定设备名，使用默认值或提示用户
        if not self.device_name:
            print("未指定设备名，尝试连接第一个可用设备...")
            try:
                self.device_name = self._get_first_device()
            except Exception as e:
                print(f"自动获取设备失败: {e}")
                print("请手动指定设备名，例如:")
                print('controller = SimpleAppiumController(device_name="your_device_id")')
                print("你可以通过 'adb devices' 命令查看设备ID")
                raise
        
        # 配置Appium选项
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = self.device_name
        options.app_package = "com.binance.dev"  # 币安App包名
        options.app_activity = "com.binance.activity.MainActivity"
        options.automation_name = "UiAutomator2"
        options.no_reset = True  # 不重置应用状态
        options.new_command_timeout = 300
        
        # Android 15权限问题解决方案
        options.ignore_hidden_api_policy_error = True  # 忽略Hidden API策略错误
        options.skip_device_initialization = True  # 跳过设备初始化
        options.skip_server_installation = True  # 跳过服务器安装
        
        # 连接设备
        try:
            self.driver = webdriver.Remote(self.appium_server, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            
            print(f"✓ 已连接设备: {self.device_name}")
            print("✓ 币安App已启动")
        except Exception as e:
            print(f"✗ 连接设备失败: {e}")
            print("请确保:")
            print("1. Appium服务器已启动 (运行: appium)")
            print("2. 设备已连接并开启USB调试")
            print("3. 币安App已安装")
            raise
        
    def _get_first_device(self):
        """获取第一个可用的Android设备"""
        import subprocess
        import os
        
        # 尝试多种adb路径
        adb_paths = [
            'adb',  # 系统PATH中的adb
            os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe'),  # 本地安装的adb
            'android-tools/platform-tools/adb.exe'  # 相对路径
        ]
        
        for adb_path in adb_paths:
            try:
                result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                    devices = [line.split()[0] for line in lines if line.strip() and 'device' in line and 'unauthorized' not in line]
                    if devices:
                        print(f"使用ADB路径: {adb_path}")
                        return devices[0]
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        raise Exception("未找到可用设备，请确保设备已连接、开启USB调试并已授权")
    
    def click_element(self, locator_type, locator_value, timeout=10):
        """点击元素"""
        try:
            if locator_type.lower() == "id":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((AppiumBy.ID, locator_value))
                )
            elif locator_type.lower() == "xpath":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, locator_value))
                )
            else:
                raise Exception(f"不支持的定位器类型: {locator_type}")
            
            element.click()
            print(f"✓ 已点击: {locator_value}")
            return True
        except Exception as e:
            print(f"✗ 点击失败: {locator_value}, 错误: {e}")
            return False
    
    def input_text(self, locator_type, locator_value, text, timeout=10):
        """输入文本"""
        try:
            if locator_type.lower() == "id":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.ID, locator_value))
                )
            elif locator_type.lower() == "xpath":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, locator_value))
                )
            else:
                raise Exception(f"不支持的定位器类型: {locator_type}")
            
            element.clear()
            element.send_keys(text)
            print(f"✓ 已输入文本: {text}")
            return True
        except Exception as e:
            print(f"✗ 输入失败: {locator_value}, 错误: {e}")
            return False
    
    def find_element(self, locator_type, locator_value):
        """查找元素"""
        try:
            if locator_type.lower() == "id":
                return self.driver.find_element(AppiumBy.ID, locator_value)
            elif locator_type.lower() == "xpath":
                return self.driver.find_element(AppiumBy.XPATH, locator_value)
            else:
                raise Exception(f"不支持的定位器类型: {locator_type}")
        except Exception as e:
            print(f"✗ 元素未找到: {locator_value}, 错误: {e}")
            return None
    
    def wait_for_element(self, locator_type, locator_value, timeout=10):
        """等待元素出现"""
        try:
            if locator_type.lower() == "id":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.ID, locator_value))
                )
            elif locator_type.lower() == "xpath":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, locator_value))
                )
            else:
                raise Exception(f"不支持的定位器类型: {locator_type}")
            
            print(f"✓ 元素已出现: {locator_value}")
            return element
        except Exception as e:
            print(f"✗ 等待元素超时: {locator_value}, 错误: {e}")
            return None
    
    def swipe(self, start_x, start_y, end_x, end_y, duration=1000):
        """滑动屏幕"""
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            print(f"✓ 滑动完成: ({start_x},{start_y}) -> ({end_x},{end_y})")
            return True
        except Exception as e:
            print(f"✗ 滑动失败: {e}")
            return False
    
    def tap(self, x, y):
        """点击坐标"""
        try:
            self.driver.tap([(x, y)])
            print(f"✓ 点击坐标: ({x},{y})")
            return True
        except Exception as e:
            print(f"✗ 点击坐标失败: {e}")
            return False
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        return self.driver.get_window_size()
    
    def take_screenshot(self, filename="screenshot.png"):
        """截屏"""
        try:
            self.driver.save_screenshot(filename)
            print(f"✓ 截屏已保存: {filename}")
            return True
        except Exception as e:
            print(f"✗ 截屏失败: {e}")
            return False
    
    def sleep(self, seconds):
        """等待"""
        print(f"等待 {seconds} 秒...")
        time.sleep(seconds)
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.quit()
            print("✓ 已断开设备连接")

def main():
    """简单的使用示例"""
    print("=== Appium手机控制器 ===")
    print("注意: 请确保Appium服务器已启动 (运行: appium)")
    
    # 你可以在这里指定设备名，例如: "emulator-5554" 或实际设备ID
    device_name = input("请输入设备名 (留空自动检测): ").strip()
    if not device_name:
        device_name = None
    
    controller = SimpleAppiumController(device_name=device_name)
    
    try:
        # 连接设备并启动币安App
        controller.connect_device()
        
        # 等待应用加载
        controller.sleep(3)
        
        # 截个屏看看当前界面
        controller.take_screenshot("binance_app.png")
        
        print("\n✓ 设备已连接，你现在可以使用以下方法控制手机:")
        print("- controller.click_element('xpath', '//按钮xpath')")
        print("- controller.input_text('id', '输入框id', '文本内容')")  
        print("- controller.tap(x, y)  # 点击坐标")
        print("- controller.swipe(x1, y1, x2, y2)  # 滑动")
        print("- controller.take_screenshot('文件名.png')")
        print("- controller.sleep(秒数)")
        
        print("\n提示: 可以在Python交互模式下使用这个controller对象")
        print("例如: controller.tap(500, 1000)")
        
        # 保持连接，让用户可以继续操作
        input("\n按回车键断开连接...")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        controller.close()

if __name__ == "__main__":
    main()