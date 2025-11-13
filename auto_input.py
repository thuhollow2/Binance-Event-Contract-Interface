#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化操作脚本：点击输入框 → 输入数字 → 关闭键盘
"""

import subprocess
import os
import time

class AutoInputController:
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
    
    def tap(self, x, y):
        """点击坐标"""
        success, _, stderr = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            print(f"✓ 点击坐标: ({x}, {y})")
            return True
        else:
            print(f"✗ 点击失败: {stderr}")
            return False
    
    def type_text(self, text):
        """输入文字"""
        # 清理文本，确保安全输入
        clean_text = str(text).replace(' ', '%s').replace('&', '\\&')
        success, _, stderr = self.run_adb(['shell', 'input', 'text', clean_text])
        if success:
            print(f"✓ 输入文字: {text}")
            return True
        else:
            print(f"✗ 输入失败: {stderr}")
            return False
    
    def hide_keyboard(self):
        """关闭键盘"""
        print("正在关闭键盘...")
        
        # 方法1: 按返回键
        success1, _, _ = self.run_adb(['shell', 'input', 'keyevent', '4'])
        if success1:
            print("✓ 键盘已关闭 (返回键)")
            return True
        
        # 方法2: 按ESC键
        success2, _, _ = self.run_adb(['shell', 'input', 'keyevent', '111'])
        if success2:
            print("✓ 键盘已关闭 (ESC键)")
            return True
        
        # 方法3: 点击输入框外的区域
        success3, _, _ = self.run_adb(['shell', 'input', 'tap', '720', '1000'])
        if success3:
            print("✓ 键盘已关闭 (点击空白)")
            return True
        
        print("✗ 关闭键盘失败")
        return False
    
    def press_enter(self):
        """按回车键"""
        success, _, _ = self.run_adb(['shell', 'input', 'keyevent', '66'])
        if success:
            print("✓ 按下回车键")
        return success
    
    def auto_input_sequence(self, number, input_box_coords=(545, 2025)):
        """自动执行完整的输入序列"""
        print(f"=== 开始自动输入序列: {number} ===")
        
        # 步骤1: 点击输入框
        print("步骤1: 点击输入框...")
        if not self.tap(input_box_coords[0], input_box_coords[1]):
            print("❌ 点击输入框失败")
            return False
        
        # 等待键盘弹出
        time.sleep(1.5)
        
        # 步骤2: 输入数字
        print(f"步骤2: 输入数字 '{number}'...")
        if not self.type_text(str(number)):
            print("❌ 输入数字失败")
            return False
        
        # 短暂等待
        time.sleep(0.5)
        
        # 步骤3: 关闭键盘
        print("步骤3: 关闭键盘...")
        if not self.hide_keyboard():
            print("❌ 关闭键盘失败")
            return False
        
        print("✅ 自动输入序列完成!")
        return True
    
    def input_with_enter(self, number, input_box_coords=(545, 2025)):
        """输入数字并按回车确认"""
        print(f"=== 输入数字并确认: {number} ===")
        
        # 点击输入框
        if not self.tap(input_box_coords[0], input_box_coords[1]):
            return False
        
        time.sleep(1)
        
        # 输入数字
        if not self.type_text(str(number)):
            return False
        
        time.sleep(0.5)
        
        # 按回车确认
        print("按回车确认...")
        if not self.press_enter():
            return False
        
        print("✅ 输入并确认完成!")
        return True

def main():
    controller = AutoInputController()
    
    print("=== 自动输入控制器 ===")
    print("这个脚本会自动执行: 点击输入框 → 输入数字 → 关闭键盘")
    
    while True:
        print("\n选择操作:")
        print("1. 输入数字并关闭键盘")
        print("2. 输入数字并按回车确认")
        print("3. 只点击第一个元素(坐标545,2025)")
        print("4. 只输入数字")
        print("5. 只关闭键盘")
        print("q. 退出")
        
        choice = input("请选择 (1-5/q): ").strip()
        
        if choice.lower() == 'q':
            break
        elif choice == '1':
            number = input("请输入数字: ").strip()
            if number:
                controller.auto_input_sequence(number)
        elif choice == '2':
            number = input("请输入数字: ").strip()
            if number:
                controller.input_with_enter(number)
        elif choice == '3':
            controller.tap(545, 2025)
        elif choice == '4':
            number = input("请输入数字: ").strip()
            if number:
                controller.type_text(number)
        elif choice == '5':
            controller.hide_keyboard()
        else:
            print("无效选择")

if __name__ == "__main__":
    main()