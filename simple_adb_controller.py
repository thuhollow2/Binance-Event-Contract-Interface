#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纯ADB点击控制器
绕过Android 15的所有限制，直接使用ADB命令控制手机
"""

import subprocess
import time
import os

class ADBClickController:
    def __init__(self, device_id="40f06c22"):
        """
        初始化ADB控制器
        
        Args:
            device_id: 设备ID
        """
        self.device_id = device_id
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        
    def run_adb(self, command):
        """执行ADB命令"""
        try:
            full_cmd = [self.adb_path, '-s', self.device_id] + command
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=15)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def connect(self):
        """检查设备连接"""
        print("检查设备连接...")
        success, stdout, stderr = self.run_adb(['devices'])
        
        if success and self.device_id in stdout and 'device' in stdout:
            print(f"✓ 设备 {self.device_id} 已连接")
            return True
        else:
            print(f"✗ 设备 {self.device_id} 未连接")
            print("请确保:")
            print("1. 手机已通过USB连接")
            print("2. 开启了USB调试")
            print("3. 已授权电脑调试")
            return False
    
    def tap(self, x, y):
        """点击坐标"""
        success, stdout, stderr = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            print(f"✓ 点击坐标: ({x}, {y})")
            return True
        else:
            print(f"✗ 点击失败: {stderr}")
            return False
    
    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动"""
        success, stdout, stderr = self.run_adb([
            'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)
        ])
        if success:
            print(f"✓ 滑动: ({x1},{y1}) -> ({x2},{y2})")
            return True
        else:
            print(f"✗ 滑动失败: {stderr}")
            return False
    
    def input_text(self, text):
        """输入文本"""
        # 处理空格和特殊字符
        escaped_text = text.replace(' ', '%s').replace('&', '\\&')
        success, stdout, stderr = self.run_adb(['shell', 'input', 'text', escaped_text])
        if success:
            print(f"✓ 输入文本: {text}")
            return True
        else:
            print(f"✗ 输入失败: {stderr}")
            return False
    
    def key_back(self):
        """返回键"""
        success, stdout, stderr = self.run_adb(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
        if success:
            print("✓ 按返回键")
            return True
        else:
            print(f"✗ 返回键失败: {stderr}")
            return False
    
    def key_home(self):
        """主页键"""
        success, stdout, stderr = self.run_adb(['shell', 'input', 'keyevent', 'KEYCODE_HOME'])
        if success:
            print("✓ 按主页键")
            return True
        else:
            print(f"✗ 主页键失败: {stderr}")
            return False
    
    def screenshot(self, filename="screenshot.png"):
        """截屏"""
        # 截屏到设备
        success1, _, _ = self.run_adb(['shell', 'screencap', '/sdcard/temp_screenshot.png'])
        if not success1:
            print("✗ 设备截屏失败")
            return False
        
        # 下载到电脑
        success2, _, _ = self.run_adb(['pull', '/sdcard/temp_screenshot.png', filename])
        if success2:
            print(f"✓ 截屏保存: {filename}")
            # 清理设备上的临时文件
            self.run_adb(['shell', 'rm', '/sdcard/temp_screenshot.png'])
            return True
        else:
            print("✗ 下载截屏失败")
            return False
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        success, stdout, stderr = self.run_adb(['shell', 'wm', 'size'])
        if success and 'Physical size:' in stdout:
            for line in stdout.split('\n'):
                if 'Physical size:' in line:
                    size_str = line.split('Physical size: ')[1].strip()
                    if 'x' in size_str:
                        width, height = size_str.split('x')
                        w, h = int(width), int(height)
                        print(f"屏幕尺寸: {w} x {h}")
                        return {"width": w, "height": h}
        
        print("使用默认屏幕尺寸")
        return {"width": 1080, "height": 2400}
    
    def wait_seconds(self, seconds):
        """等待"""
        print(f"等待 {seconds} 秒...")
        time.sleep(seconds)

def main():
    """主函数"""
    print("=== ADB点击控制器 ===")
    print("使用纯ADB命令，无需复杂权限")
    print("适用于Android 15及所有版本")
    print()
    
    controller = ADBClickController()
    
    if not controller.connect():
        return
    
    # 获取屏幕信息
    size = controller.get_screen_size()
    center_x, center_y = size["width"] // 2, size["height"] // 2
    
    print(f"屏幕中心点: ({center_x}, {center_y})")
    
    # 截屏查看当前状态
    controller.screenshot("start_screen.png")
    
    print("\n现在请手动打开币安App")
    input("打开币安App后按回车继续...")
    
    controller.screenshot("binance_opened.png")
    
    print("\n=== ADB控制器就绪 ===")
    print("可用命令:")
    print("tap(x, y) - 点击坐标")
    print("swipe(x1, y1, x2, y2) - 滑动")
    print("type('文本') - 输入文本")
    print("screenshot('文件名') - 截屏")
    print("back() - 返回键")
    print("home() - 主页键")
    print("wait(秒数) - 等待")
    print("center() - 点击屏幕中心")
    print("up() - 向上滑动")
    print("down() - 向下滑动")
    print("quit - 退出")
    print()
    
    # 交互控制循环
    while True:
        try:
            cmd = input("ADB >>> ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                break
            elif cmd == 'back()':
                controller.key_back()
            elif cmd == 'home()':
                controller.key_home()
            elif cmd == 'center()':
                controller.tap(center_x, center_y)
            elif cmd == 'up()':
                # 向上滑动
                controller.swipe(center_x, center_y + 300, center_x, center_y - 300)
            elif cmd == 'down()':
                # 向下滑动
                controller.swipe(center_x, center_y - 300, center_x, center_y + 300)
            elif cmd.startswith('tap(') and cmd.endswith(')'):
                try:
                    coords = cmd[4:-1].split(',')
                    if len(coords) == 2:
                        x, y = int(coords[0].strip()), int(coords[1].strip())
                        controller.tap(x, y)
                except ValueError:
                    print("坐标格式错误，请使用: tap(x, y)")
            elif cmd.startswith('swipe(') and cmd.endswith(')'):
                try:
                    coords = cmd[6:-1].split(',')
                    if len(coords) >= 4:
                        x1, y1, x2, y2 = [int(c.strip()) for c in coords[:4]]
                        controller.swipe(x1, y1, x2, y2)
                except ValueError:
                    print("滑动格式错误，请使用: swipe(x1, y1, x2, y2)")
            elif cmd.startswith("type('") and cmd.endswith("')"):
                text = cmd[6:-2]
                controller.input_text(text)
            elif cmd.startswith('screenshot(') and cmd.endswith(')'):
                filename = cmd[11:-1].strip().strip('"\'') or "screenshot.png"
                controller.screenshot(filename)
            elif cmd.startswith('wait(') and cmd.endswith(')'):
                try:
                    seconds = float(cmd[5:-1])
                    controller.wait_seconds(seconds)
                except ValueError:
                    print("等待时间格式错误")
            elif cmd == 'help':
                print("命令示例:")
                print("tap(500, 1000) - 点击坐标500,1000")
                print("swipe(500, 1500, 500, 500) - 从下往上滑动")
                print("type('hello') - 输入hello")
                print("screenshot('test.png') - 截屏")
                print("center() - 点击屏幕中心")
            elif cmd:
                print("未知命令，输入 help 查看帮助")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"命令执行错误: {e}")
    
    print("\n✓ ADB控制器已退出")

if __name__ == "__main__":
    main()