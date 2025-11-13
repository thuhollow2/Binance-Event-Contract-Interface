#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速点击工具 - 无需扫描直接点击
"""

import subprocess
import os
import time
import re

class QuickClick:
    def __init__(self, device_id="40f06c22"):
        self.device_id = device_id
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        
    def run_adb(self, command):
        """执行ADB命令"""
        try:
            full_cmd = [self.adb_path, '-s', self.device_id] + command
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def tap(self, x, y):
        """直接点击坐标"""
        success, _, stderr = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            print(f"✓ 点击: ({x}, {y})")
        else:
            print(f"✗ 点击失败: {stderr}")
        return success
    
    def type_text(self, text):
        """输入文字"""
        escaped_text = str(text).replace(' ', '%s').replace('&', '\\&')
        success, _, _ = self.run_adb(['shell', 'input', 'text', escaped_text])
        if success:
            print(f"✓ 输入: {text}")
        return success
    
    def press_key(self, key_code):
        """按键"""
        success, _, _ = self.run_adb(['shell', 'input', 'keyevent', str(key_code)])
        return success
    
    def click_text_fast(self, text, nth=1):
        """快速通过文本点击 (不扫描UI，直接查找)"""
        print(f"🔍 快速查找文本: '{text}' (第{nth}个)")
        
        # 快速获取UI dump
        success, _, _ = self.run_adb(['shell', 'uiautomator', 'dump'])
        if not success:
            print("✗ 获取UI失败")
            return False
        
        # 直接读取设备上的XML
        success, xml_content, _ = self.run_adb(['shell', 'cat', '/sdcard/window_dump.xml'])
        if not success:
            print("✗ 读取UI文件失败")
            return False
        
        # 快速解析查找文本
        matches = []
        pattern = r'<node[^>]*text="[^"]*' + re.escape(text) + r'[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*>'
        
        for match in re.finditer(pattern, xml_content, re.IGNORECASE):
            x1, y1, x2, y2 = map(int, match.groups())
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            matches.append((center_x, center_y))
        
        if matches and nth <= len(matches):
            x, y = matches[nth - 1]
            print(f"✓ 找到文本位置: ({x}, {y})")
            return self.tap(x, y)
        else:
            print(f"✗ 未找到第{nth}个 '{text}'，共找到{len(matches)}个")
            return False
    
    def quick_binance_actions(self):
        """币安常用操作的预设坐标"""
        actions = {
            # 基于你之前扫描的结果设置常用坐标
            'input': (545, 2025),      # 输入框
            'btn1': (1088, 2025),      # 第一个按钮
            'btn2': (1294, 2025),      # 第二个按钮
            'up1': (811, 385),         # 上涨: 80%
            'up2': (416, 2452),        # 上涨按钮
            'down': (1099, 2452),      # 下跌按钮
            'ma': (67, 1533),          # MA指标
            'ema': (215, 1533),        # EMA指标
            '1min': (91, 526),         # 1分钟
            '5min': (221, 526),        # 5分钟
            '1hour': (831, 526),       # 1小时
        }
        return actions
    
    def click_preset(self, preset_name):
        """点击预设位置"""
        actions = self.quick_binance_actions()
        if preset_name in actions:
            x, y = actions[preset_name]
            print(f"🎯 预设点击: {preset_name}")
            return self.tap(x, y)
        else:
            print(f"✗ 未知预设: {preset_name}")
            print(f"可用预设: {', '.join(actions.keys())}")
            return False
    
    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动"""
        success, _, _ = self.run_adb(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)])
        if success:
            print(f"✓ 滑动: ({x1},{y1}) → ({x2},{y2})")
        return success
    
    def interactive_mode(self):
        """交互模式"""
        print("🚀 快速点击工具")
        print("无需扫描，直接操作！")
        
        while True:
            print("\n💡 快速命令:")
            print("tap x y - 直接点击坐标")
            print("text '文本' [数字] - 快速查找文本点击") 
            print("preset 名称 - 点击预设位置")
            print("type '文本' - 输入文字")
            print("enter/back/hide - 按键操作")
            print("presets - 显示所有预设")
            print("auto '数字' - 自动输入数字流程")
            print("quit - 退出")
            
            cmd = input("\n快速点击 >>> ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                break
            elif cmd.startswith('tap '):
                try:
                    parts = cmd.split()
                    if len(parts) >= 3:
                        x, y = int(parts[1]), int(parts[2])
                        self.tap(x, y)
                except ValueError:
                    print("格式: tap x y")
            elif cmd.startswith('text '):
                parts = cmd[5:].split()
                if parts:
                    text = parts[0].strip('"\'')
                    nth = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    self.click_text_fast(text, nth)
            elif cmd.startswith('preset '):
                preset = cmd[7:].strip()
                self.click_preset(preset)
            elif cmd.startswith('type '):
                text = cmd[5:].strip().strip('"\'')
                if text:
                    self.type_text(text)
            elif cmd == 'enter':
                self.press_key(66)
                print("✓ 回车")
            elif cmd == 'back':
                self.press_key(4)
                print("✓ 返回")
            elif cmd == 'hide':
                self.press_key(4)  # 返回键关闭键盘
                print("✓ 关闭键盘")
            elif cmd == 'presets':
                actions = self.quick_binance_actions()
                print("📋 可用预设:")
                for name, (x, y) in actions.items():
                    print(f"  {name:8} - ({x:4}, {y:4})")
            elif cmd.startswith('auto '):
                number = cmd[5:].strip()
                if number:
                    print(f"🎯 自动输入流程: {number}")
                    # 点击输入框 -> 输入数字 -> 关闭键盘
                    if self.click_preset('input'):
                        time.sleep(0.5)
                        if self.type_text(number):
                            time.sleep(0.3)
                            self.press_key(4)  # 关闭键盘
                            print("✅ 自动输入完成")
            elif cmd:
                print("❌ 未知命令")

def main():
    clicker = QuickClick()
    clicker.interactive_mode()

if __name__ == "__main__":
    main()