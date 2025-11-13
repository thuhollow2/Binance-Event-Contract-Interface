#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的Appium控制器
不启动特定应用，直接控制设备
"""

import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

class MinimalAppiumController:
    def __init__(self, device_name="40f06c22", appium_server="http://localhost:4723"):
        self.device_name = device_name
        self.appium_server = appium_server
        self.driver = None
        
    def connect_device(self):
        """最简单的设备连接"""
        print("正在连接设备...")
        print(f"设备ID: {self.device_name}")
        
        # 最简配置 - 不启动特定应用
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = self.device_name
        options.automation_name = "UiAutomator2"
        
        # 关键设置 - 不启动应用
        options.no_reset = True
        options.new_command_timeout = 300
        options.ignore_hidden_api_policy_error = True
        
        try:
            self.driver = webdriver.Remote(self.appium_server, options=options)
            print("✓ 设备连接成功")
            print("✓ 现在可以控制设备了")
            return True
            
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    def launch_binance(self):
        """手动启动币安App"""
        try:
            self.driver.start_activity("com.binance.dev", "com.binance.activity.MainActivity")
            print("✓ 币安App已启动")
            return True
        except Exception as e:
            print(f"✗ 启动币安App失败: {e}")
            # 尝试备用包名
            try:
                self.driver.start_activity("com.binance.android", ".activity.MainActivity")
                print("✓ 币安App已启动 (备用包名)")
                return True
            except:
                print("请手动打开币安App")
                return False
    
    def tap(self, x, y):
        """点击坐标"""
        try:
            self.driver.tap([(x, y)])
            print(f"✓ 点击: ({x}, {y})")
            return True
        except Exception as e:
            print(f"✗ 点击失败: {e}")
            return False
    
    def swipe(self, x1, y1, x2, y2, duration=1000):
        """滑动"""
        try:
            self.driver.swipe(x1, y1, x2, y2, duration)
            print(f"✓ 滑动: ({x1},{y1}) -> ({x2},{y2})")
            return True
        except Exception as e:
            print(f"✗ 滑动失败: {e}")
            return False
    
    def screenshot(self, filename="screenshot.png"):
        """截屏"""
        try:
            self.driver.save_screenshot(filename)
            print(f"✓ 截屏: {filename}")
            return True
        except Exception as e:
            print(f"✗ 截屏失败: {e}")
            return False
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        try:
            size = self.driver.get_window_size()
            print(f"屏幕: {size['width']} x {size['height']}")
            return size
        except Exception as e:
            print(f"✗ 获取屏幕尺寸失败: {e}")
            return {"width": 1080, "height": 2400}  # 默认值
    
    def press_back(self):
        """按返回键"""
        try:
            self.driver.back()
            print("✓ 按下返回键")
            return True
        except Exception as e:
            print(f"✗ 返回键失败: {e}")
            return False
    
    def press_home(self):
        """按主页键"""
        try:
            self.driver.press_keycode(3)  # HOME键
            print("✓ 按下主页键")
            return True
        except Exception as e:
            print(f"✗ 主页键失败: {e}")
            return False
    
    def get_current_activity(self):
        """获取当前活动的应用"""
        try:
            activity = self.driver.current_activity
            print(f"当前活动: {activity}")
            return activity
        except Exception as e:
            print(f"✗ 获取当前活动失败: {e}")
            return None
    
    def close(self):
        """关闭连接"""
        try:
            if self.driver:
                self.driver.quit()
                print("✓ 连接已关闭")
        except:
            pass

def main():
    print("=== 最简Appium控制器 ===")
    print("直接连接设备，不启动特定应用")
    print()
    
    controller = MinimalAppiumController()
    
    try:
        if not controller.connect_device():
            return
        
        # 获取屏幕信息
        size = controller.get_screen_size()
        
        # 尝试启动币安App
        print("\n尝试启动币安App...")
        if not controller.launch_binance():
            input("请手动打开币安App，然后按回车继续...")
        
        # 等待一下
        time.sleep(3)
        
        # 截屏看看当前状态
        controller.screenshot("current_screen.png")
        
        # 获取当前活动
        controller.get_current_activity()
        
        print("\n=== 控制器已就绪 ===")
        print("可用命令:")
        print("tap(x, y) - 点击坐标") 
        print("swipe(x1, y1, x2, y2) - 滑动")
        print("screenshot('name.png') - 截屏")
        print("back() - 返回键")
        print("home() - 主页键")
        print("binance() - 启动币安App")
        print("quit - 退出")
        
        # 简化的交互模式
        while True:
            try:
                cmd = input("\n>>> ").strip()
                
                if cmd.lower() in ['quit', 'exit', 'q']:
                    break
                elif cmd == 'back()':
                    controller.press_back()
                elif cmd == 'home()':
                    controller.press_home()
                elif cmd == 'binance()':
                    controller.launch_binance()
                elif cmd.startswith('tap(') and cmd.endswith(')'):
                    coords = cmd[4:-1].split(',')
                    if len(coords) == 2:
                        x, y = int(coords[0].strip()), int(coords[1].strip())
                        controller.tap(x, y)
                elif cmd.startswith('swipe(') and cmd.endswith(')'):
                    coords = cmd[6:-1].split(',')
                    if len(coords) >= 4:
                        x1, y1, x2, y2 = [int(c.strip()) for c in coords[:4]]
                        controller.swipe(x1, y1, x2, y2)
                elif cmd.startswith('screenshot(') and cmd.endswith(')'):
                    filename = cmd[11:-1].strip().strip('"\'') or "screenshot.png"
                    controller.screenshot(filename)
                elif cmd == 'help':
                    print("示例:")
                    print("tap(500, 1000)")
                    print("swipe(500, 1500, 500, 500)") 
                    print("screenshot('test.png')")
                elif cmd:
                    print("输入 help 查看命令格式")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"命令错误: {e}")
        
    except Exception as e:
        print(f"运行错误: {e}")
    finally:
        controller.close()

if __name__ == "__main__":
    main()