#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纯坐标控制器 - 绕过Android 15的限制
使用最基本的ADB命令直接控制手机
"""

import subprocess
import time
import os

class PureADBController:
    def __init__(self, device_id="40f06c22"):
        self.device_id = device_id
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        
    def run_adb_command(self, command):
        """运行ADB命令"""
        try:
            full_command = [self.adb_path, '-s', self.device_id] + command
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def check_device(self):
        """检查设备连接"""
        success, stdout, stderr = self.run_adb_command(['devices'])
        if success and self.device_id in stdout:
            print(f"✓ 设备 {self.device_id} 已连接")
            return True
        else:
            print(f"✗ 设备 {self.device_id} 未连接")
            return False
    
    def tap(self, x, y):
        """点击坐标"""
        success, stdout, stderr = self.run_adb_command(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            print(f"✓ 点击: ({x}, {y})")
            return True
        else:
            print(f"✗ 点击失败: {stderr}")
            return False
    
    def swipe(self, x1, y1, x2, y2, duration=1000):
        """滑动"""
        success, stdout, stderr = self.run_adb_command([
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
        # 替换空格和特殊字符
        text = text.replace(' ', '%s')
        success, stdout, stderr = self.run_adb_command(['shell', 'input', 'text', text])
        if success:
            print(f"✓ 输入文本: {text}")
            return True
        else:
            print(f"✗ 输入失败: {stderr}")
            return False
    
    def press_back(self):
        """按返回键"""
        success, stdout, stderr = self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
        if success:
            print("✓ 按下返回键")
            return True
        else:
            print(f"✗ 返回键失败: {stderr}")
            return False
    
    def press_home(self):
        """按主页键"""
        success, stdout, stderr = self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_HOME'])
        if success:
            print("✓ 按下主页键")
            return True
        else:
            print(f"✗ 主页键失败: {stderr}")
            return False
    
    def press_menu(self):
        """按菜单键"""
        success, stdout, stderr = self.run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_MENU'])
        if success:
            print("✓ 按下菜单键")
            return True
        else:
            print(f"✗ 菜单键失败: {stderr}")
            return False
    
    def screenshot(self, filename="screenshot.png"):
        """截屏"""
        # 先截屏到设备
        success1, _, _ = self.run_adb_command(['shell', 'screencap', '/sdcard/screenshot.png'])
        if not success1:
            print("✗ 截屏失败")
            return False
        
        # 然后下载到电脑
        success2, _, _ = self.run_adb_command(['pull', '/sdcard/screenshot.png', filename])
        if success2:
            print(f"✓ 截屏保存: {filename}")
            return True
        else:
            print(f"✗ 下载截屏失败")
            return False
    
    def get_screen_size(self):
        """获取屏幕分辨率"""
        success, stdout, stderr = self.run_adb_command(['shell', 'wm', 'size'])
        if success and 'Physical size:' in stdout:
            size_line = [line for line in stdout.split('\n') if 'Physical size:' in line][0]
            size_str = size_line.split('Physical size: ')[1].strip()
            width, height = size_str.split('x')
            w, h = int(width), int(height)
            print(f"屏幕尺寸: {w} x {h}")
            return {"width": w, "height": h}
        else:
            print("✗ 获取屏幕尺寸失败")
            return {"width": 1080, "height": 2400}  # 默认值
    
    def start_app(self, package_name, activity_name=None):
        """启动应用"""
        if activity_name:
            cmd = ['shell', 'am', 'start', '-n', f'{package_name}/{activity_name}']
        else:
            cmd = ['shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1']
        
        success, stdout, stderr = self.run_adb_command(cmd)
        if success:
            print(f"✓ 启动应用: {package_name}")
            return True
        else:
            print(f"✗ 启动应用失败: {stderr}")
            return False
    
    def get_current_app(self):
        """获取当前应用包名"""
        success, stdout, stderr = self.run_adb_command([
            'shell', 'dumpsys', 'window', 'windows', '|', 'grep', '-E', 'mCurrentFocus'
        ])
        if success:
            print(f"当前焦点: {stdout.strip()}")
            return stdout.strip()
        else:
            return "未知"

def main():
    print("=== 纯ADB控制器 ===")
    print("使用ADB命令直接控制，绕过Android 15限制")
    print()
    
    controller = PureADBController()
    
    if not controller.check_device():
        print("设备未连接，请检查USB连接和调试权限")
        return
    
    # 获取屏幕信息
    size = controller.get_screen_size()
    
    # 截个屏看看当前状态
    controller.screenshot("current.png")
    
    # 尝试启动币安App
    print("\n尝试启动币安App...")
    binance_started = (
        controller.start_app("com.binance.dev", "com.binance.activity.MainActivity") or
        controller.start_app("com.binance.android", ".activity.MainActivity") or
        controller.start_app("com.binance.dev")  # 使用monkey命令
    )
    
    if not binance_started:
        print("自动启动失败，请手动打开币安App")
        input("打开币安App后按回车继续...")
    
    time.sleep(3)
    controller.screenshot("after_binance.png")
    
    print("\n=== 纯ADB控制器就绪 ===")
    print("所有操作都通过ADB命令执行，无需额外权限")
    print("\n可用命令:")
    print("tap(x, y) - 点击坐标")
    print("swipe(x1, y1, x2, y2) - 滑动")
    print("type('文本') - 输入文本")
    print("screenshot('文件名') - 截屏")
    print("back() - 返回键")
    print("home() - 主页键")
    print("menu() - 菜单键")
    print("binance() - 启动币安App")
    print("size() - 获取屏幕尺寸")
    print("quit - 退出")
    
    # 交互模式
    while True:
        try:
            cmd = input(f"\nADB[{controller.device_id}] >>> ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                break
            elif cmd == 'back()':
                controller.press_back()
            elif cmd == 'home()':
                controller.press_home()
            elif cmd == 'menu()':
                controller.press_menu()
            elif cmd == 'size()':
                controller.get_screen_size()
            elif cmd == 'binance()':
                controller.start_app("com.binance.dev")
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
            elif cmd.startswith('type(') and cmd.endswith(')'):
                text = cmd[5:-1].strip().strip('"\'')
                controller.input_text(text)
            elif cmd.startswith('screenshot(') and cmd.endswith(')'):
                filename = cmd[11:-1].strip().strip('"\'') or "screenshot.png"
                controller.screenshot(filename)
            elif cmd == 'help':
                print("命令示例:")
                print("tap(500, 1000)")
                print("swipe(500, 1500, 500, 500)")
                print("type('hello world')")
                print("screenshot('test.png')")
            elif cmd:
                print("未知命令，输入 help 查看帮助")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"命令错误: {e}")
    
    print("✓ 已退出ADB控制器")

if __name__ == "__main__":
    main()