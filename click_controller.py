#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简洁的Appium控制器 - 只连接设备，不启动应用
用户手动打开币安App，然后使用控制器点击按钮
"""

import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SimpleClickController:
    def __init__(self, device_name="40f06c22", appium_server="http://localhost:4723"):
        """
        简洁的点击控制器
        
        Args:
            device_name: 设备名称
            appium_server: Appium服务器地址
        """
        self.device_name = device_name
        self.appium_server = appium_server
        self.driver = None
        self.wait = None
        
    def connect(self):
        """连接设备 - 不启动任何应用"""
        print("正在连接设备...")
        print(f"设备ID: {self.device_name}")
        
        # 最简配置 - 只连接设备，不启动应用
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = self.device_name
        options.automation_name = "UiAutomator2"
        
        # Android 15兼容设置
        options.no_reset = True
        options.new_command_timeout = 300
        options.ignore_hidden_api_policy_error = True
        options.skip_device_initialization = True
        options.skip_server_installation = True
        
        try:
            self.driver = webdriver.Remote(self.appium_server, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            
            print("✓ 设备连接成功")
            print("✓ 可以开始控制了")
            return True
            
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            print("\n请确保:")
            print("1. Appium服务器正在运行 (appium)")
            print("2. 设备已连接并开启USB调试")
            return False
    
    def click_by_text(self, text, timeout=5):
        """通过文本点击元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, f"//*[contains(@text, '{text}')]"))
            )
            element.click()
            print(f"✓ 点击文本: {text}")
            return True
        except Exception as e:
            print(f"✗ 未找到文本: {text}")
            return False
    
    def click_by_id(self, resource_id, timeout=5):
        """通过ID点击元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.ID, resource_id))
            )
            element.click()
            print(f"✓ 点击ID: {resource_id}")
            return True
        except Exception as e:
            print(f"✗ 未找到ID: {resource_id}")
            return False
    
    def click_by_xpath(self, xpath, timeout=5):
        """通过XPath点击元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
            )
            element.click()
            print(f"✓ 点击XPath: {xpath}")
            return True
        except Exception as e:
            print(f"✗ 未找到XPath: {xpath}")
            return False
    
    def tap_coordinate(self, x, y):
        """点击坐标"""
        try:
            self.driver.tap([(x, y)])
            print(f"✓ 点击坐标: ({x}, {y})")
            return True
        except Exception as e:
            print(f"✗ 点击坐标失败: {e}")
            return False
    
    def input_text_by_id(self, resource_id, text, timeout=5):
        """通过ID输入文本"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.ID, resource_id))
            )
            element.clear()
            element.send_keys(text)
            print(f"✓ 输入文本到ID {resource_id}: {text}")
            return True
        except Exception as e:
            print(f"✗ 输入失败: {e}")
            return False
    
    def input_text_by_xpath(self, xpath, text, timeout=5):
        """通过XPath输入文本"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, xpath))
            )
            element.clear()
            element.send_keys(text)
            print(f"✓ 输入文本: {text}")
            return True
        except Exception as e:
            print(f"✗ 输入失败: {e}")
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
        """等待"""
        print(f"等待 {seconds} 秒...")
        time.sleep(seconds)
    
    def get_current_activity(self):
        """获取当前活动"""
        try:
            activity = self.driver.current_activity
            print(f"当前活动: {activity}")
            return activity
        except Exception as e:
            print(f"✗ 获取活动失败: {e}")
            return None
    
    def find_elements_by_text(self, text):
        """查找所有包含指定文本的元素"""
        try:
            elements = self.driver.find_elements(AppiumBy.XPATH, f"//*[contains(@text, '{text}')]")
            print(f"找到 {len(elements)} 个包含文本 '{text}' 的元素")
            return elements
        except Exception as e:
            print(f"✗ 查找元素失败: {e}")
            return []
    
    def close(self):
        """关闭连接"""
        try:
            if self.driver:
                self.driver.quit()
                print("✓ 连接已关闭")
        except Exception as e:
            print(f"关闭连接出错: {e}")

def main():
    """主函数 - 交互式控制器"""
    print("=== 简洁Appium点击控制器 ===")
    print("只连接设备，不自动启动应用")
    print("请手动打开你需要控制的应用")
    print()
    
    controller = SimpleClickController()
    
    try:
        if not controller.connect():
            return
        
        print("\n设备已连接！")
        print("请手动打开币安App或其他你想控制的应用")
        input("打开应用后按回车继续...")
        
        # 截屏看当前状态
        controller.screenshot("current_screen.png")
        
        print("\n=== 控制器就绪 ===")
        print("可用命令:")
        print("text('按钮文字') - 点击包含文字的按钮")
        print("id('元素ID') - 点击指定ID的元素")  
        print("xpath('xpath路径') - 点击XPath元素")
        print("tap(x, y) - 点击坐标")
        print("input_id('ID', '文本') - 在指定ID输入框输入")
        print("swipe(x1, y1, x2, y2) - 滑动")
        print("screenshot('文件名') - 截屏")
        print("wait(秒数) - 等待")
        print("activity() - 获取当前活动")
        print("quit - 退出")
        print()
        
        # 交互模式
        while True:
            try:
                cmd = input("控制器 >>> ").strip()
                
                if cmd.lower() in ['quit', 'exit', 'q']:
                    break
                elif cmd.startswith("text('") and cmd.endswith("')"):
                    text = cmd[6:-2]
                    controller.click_by_text(text)
                elif cmd.startswith('id("') and cmd.endswith('")'):
                    element_id = cmd[4:-2]
                    controller.click_by_id(element_id)
                elif cmd.startswith("xpath('") and cmd.endswith("')"):
                    xpath = cmd[7:-2]
                    controller.click_by_xpath(xpath)
                elif cmd.startswith('tap(') and cmd.endswith(')'):
                    coords = cmd[4:-1].split(',')
                    if len(coords) == 2:
                        x, y = int(coords[0].strip()), int(coords[1].strip())
                        controller.tap_coordinate(x, y)
                elif cmd.startswith('input_id(') and cmd.endswith(')'):
                    # 解析 input_id('id', 'text') 格式
                    params = cmd[9:-1]
                    parts = params.split("',")
                    if len(parts) == 2:
                        element_id = parts[0].strip().strip("'\"")
                        text = parts[1].strip().strip("'\"")
                        controller.input_text_by_id(element_id, text)
                elif cmd.startswith('swipe(') and cmd.endswith(')'):
                    coords = cmd[6:-1].split(',')
                    if len(coords) >= 4:
                        x1, y1, x2, y2 = [int(c.strip()) for c in coords[:4]]
                        controller.swipe(x1, y1, x2, y2)
                elif cmd.startswith("screenshot('") and cmd.endswith("')"):
                    filename = cmd[12:-2] or "screenshot.png"
                    controller.screenshot(filename)
                elif cmd.startswith('wait(') and cmd.endswith(')'):
                    seconds = int(cmd[5:-1])
                    controller.wait_seconds(seconds)
                elif cmd == 'activity()':
                    controller.get_current_activity()
                elif cmd == 'help':
                    print("命令示例:")
                    print("text('登录') - 点击登录按钮")
                    print("id('com.example:id/button') - 点击指定ID")
                    print("tap(500, 1000) - 点击坐标")
                    print("input_id('edit_text', 'hello') - 输入文本")
                elif cmd:
                    print("未知命令，输入 help 查看帮助")
                    
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