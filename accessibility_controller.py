#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无障碍服务方案 - 绕过Android 15输入权限限制
通过启用无障碍服务来实现点击控制
"""

import subprocess
import time
import os

class AccessibilityController:
    def __init__(self, device_id="40f06c22"):
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
    
    def check_device(self):
        """检查设备连接"""
        success, stdout, stderr = self.run_adb(['devices'])
        if success and self.device_id in stdout:
            print(f"✓ 设备 {self.device_id} 已连接")
            return True
        else:
            print(f"✗ 设备未连接")
            return False
    
    def enable_accessibility_settings(self):
        """引导用户启用无障碍服务"""
        print("\n=== 启用无障碍服务解决方案 ===")
        print("Android 15 需要特殊权限，请按以下步骤操作：")
        print()
        print("1. 在手机上打开 '设置' 应用")
        print("2. 进入 '无障碍' 或 '辅助功能'")  
        print("3. 找到 'TalkBack' 或 'Voice Assistant'")
        print("4. 临时启用 TalkBack（用完后可关闭）")
        print()
        print("启用后，我们可以使用无障碍API来控制手机")
        print()
        
        # 尝试直接打开无障碍设置
        success, _, _ = self.run_adb(['shell', 'am', 'start', '-a', 'android.settings.ACCESSIBILITY_SETTINGS'])
        if success:
            print("✓ 已打开无障碍设置页面")
        else:
            print("请手动打开: 设置 -> 无障碍")
        
        input("启用无障碍服务后按回车继续...")
    
    def try_accessibility_tap(self, x, y):
        """使用无障碍服务点击"""
        # 方法1: 使用无障碍全局手势
        cmd1 = ['shell', 'cmd', 'accessibility', 'call-service', 'com.android.talkback/.TalkBackService', '1', 'android.accessibilityservice:gesture', f'{x},{y}']
        success1, stdout1, stderr1 = self.run_adb(cmd1)
        
        if success1:
            print(f"✓ 无障碍点击: ({x}, {y})")
            return True
        
        # 方法2: 使用sendevent模拟触摸
        return self.simulate_touch_events(x, y)
    
    def simulate_touch_events(self, x, y):
        """模拟底层触摸事件"""
        try:
            # 获取触摸设备
            success, stdout, _ = self.run_adb(['shell', 'getevent', '-t'])
            if not success:
                return False
            
            # 使用sendevent发送触摸事件序列
            commands = [
                ['shell', 'sendevent', '/dev/input/event1', '3', '57', '0'],  # 触摸开始
                ['shell', 'sendevent', '/dev/input/event1', '1', '330', '1'],  # 触摸按下
                ['shell', 'sendevent', '/dev/input/event1', '3', '53', str(x)],  # X坐标
                ['shell', 'sendevent', '/dev/input/event1', '3', '54', str(y)],  # Y坐标
                ['shell', 'sendevent', '/dev/input/event1', '0', '0', '0'],  # 同步
                ['shell', 'sendevent', '/dev/input/event1', '1', '330', '0'],  # 触摸抬起
                ['shell', 'sendevent', '/dev/input/event1', '3', '57', '-1'],  # 触摸结束
                ['shell', 'sendevent', '/dev/input/event1', '0', '0', '0'],  # 同步
            ]
            
            for cmd in commands:
                success, _, _ = self.run_adb(cmd)
                if not success:
                    print(f"✗ sendevent失败")
                    return False
                time.sleep(0.01)
            
            print(f"✓ 底层触摸事件: ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"✗ 模拟触摸失败: {e}")
            return False
    
    def try_monkey_tap(self, x, y):
        """使用monkey工具点击"""
        success, stdout, stderr = self.run_adb([
            'shell', 'monkey', '-p', 'com.android.systemui', '-c', 'android.intent.category.HOME', '1'
        ])
        
        if success:
            # 使用monkey发送触摸事件
            success2, _, _ = self.run_adb([
                'shell', 'monkey', '--pct-touch', '100', '--throttle', '100', '1'
            ])
            if success2:
                print(f"✓ Monkey点击: ({x}, {y})")
                return True
        
        print(f"✗ Monkey点击失败")
        return False
    
    def screenshot(self, filename="screenshot.png"):
        """截屏"""
        success1, _, _ = self.run_adb(['shell', 'screencap', '/sdcard/temp.png'])
        if success1:
            success2, _, _ = self.run_adb(['pull', '/sdcard/temp.png', filename])
            if success2:
                print(f"✓ 截屏: {filename}")
                self.run_adb(['shell', 'rm', '/sdcard/temp.png'])
                return True
        
        print("✗ 截屏失败")
        return False
    
    def get_screen_info(self):
        """获取屏幕信息"""
        success, stdout, _ = self.run_adb(['shell', 'wm', 'size'])
        if success and 'Physical size:' in stdout:
            for line in stdout.split('\n'):
                if 'Physical size:' in line:
                    size_str = line.split('Physical size: ')[1].strip()
                    if 'x' in size_str:
                        width, height = size_str.split('x')
                        return int(width), int(height)
        return 1080, 2400  # 默认值

def main():
    print("=== Android 15 兼容控制器 ===")
    print("使用多种方法绕过输入权限限制")
    
    controller = AccessibilityController()
    
    if not controller.check_device():
        return
    
    # 获取屏幕信息
    width, height = controller.get_screen_info()
    print(f"屏幕尺寸: {width} x {height}")
    
    # 引导启用无障碍服务
    controller.enable_accessibility_settings()
    
    # 截屏看当前状态
    controller.screenshot("current_state.png")
    
    print("\n=== 多方法控制器就绪 ===")
    print("将尝试以下方法进行点击:")
    print("1. 无障碍服务API")
    print("2. 底层sendevent")  
    print("3. Monkey工具")
    print()
    print("可用命令:")
    print("tap(x, y) - 智能点击（尝试多种方法）")
    print("screenshot('文件名') - 截屏")
    print("center() - 点击屏幕中心")
    print("test() - 测试所有点击方法")
    print("quit - 退出")
    
    center_x, center_y = width // 2, height // 2
    
    while True:
        try:
            cmd = input("\n多方法控制器 >>> ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                break
            elif cmd == 'center()':
                # 尝试所有方法点击中心
                print(f"尝试点击屏幕中心: ({center_x}, {center_y})")
                if not controller.try_accessibility_tap(center_x, center_y):
                    controller.try_monkey_tap(center_x, center_y)
            elif cmd == 'test()':
                print("测试所有点击方法...")
                test_x, test_y = center_x, center_y + 200
                print(f"测试点击: ({test_x}, {test_y})")
                
                controller.try_accessibility_tap(test_x, test_y)
                time.sleep(1)
                controller.try_monkey_tap(test_x, test_y)
                
            elif cmd.startswith('tap(') and cmd.endswith(')'):
                try:
                    coords = cmd[4:-1].split(',')
                    if len(coords) == 2:
                        x, y = int(coords[0].strip()), int(coords[1].strip())
                        print(f"尝试智能点击: ({x}, {y})")
                        
                        # 按优先级尝试不同方法
                        if not controller.try_accessibility_tap(x, y):
                            controller.try_monkey_tap(x, y)
                except ValueError:
                    print("坐标格式错误")
                    
            elif cmd.startswith('screenshot(') and cmd.endswith(')'):
                filename = cmd[11:-1].strip().strip('"\'') or "screenshot.png"
                controller.screenshot(filename)
                
            elif cmd == 'help':
                print("尝试这些命令:")
                print("center() - 点击屏幕中心")
                print("tap(500, 1000) - 点击指定坐标")  
                print("test() - 测试所有方法")
                
            elif cmd:
                print("输入 help 查看帮助")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"执行错误: {e}")
    
    print("\n✓ 控制器已退出")

if __name__ == "__main__":
    main()