#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版ADB控制器 - 集成元素查找功能
"""

import subprocess
import os
import json
import re
import time

class SmartController:
    def __init__(self, device_id="40f06c22"):
        self.device_id = device_id
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        self.last_elements = []
        
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
        success, stdout, stderr = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            print(f"✓ 点击坐标: ({x}, {y})")
            return True
        else:
            print(f"✗ 点击失败: {stderr}")
            return False
    
    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动手势"""
        success, stdout, stderr = self.run_adb(['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)])
        if success:
            print(f"✓ 滑动: ({x1},{y1}) → ({x2},{y2})")
            return True
        return False
    
    def type_text(self, text):
        """输入文字"""
        # 对特殊字符进行转义
        escaped_text = text.replace(' ', '%s').replace('&', '\&')
        success, _, _ = self.run_adb(['shell', 'input', 'text', escaped_text])
        if success:
            print(f"✓ 输入文字: {text}")
        return success
    
    def press_key(self, key_code):
        """按键 (例如: KEYCODE_BACK=4, KEYCODE_HOME=3)"""
        success, _, _ = self.run_adb(['shell', 'input', 'keyevent', str(key_code)])
        return success
    
    def screenshot(self, filename="current.png"):
        """截屏"""
        success1, _, _ = self.run_adb(['shell', 'screencap', '/sdcard/temp.png'])
        if success1:
            success2, _, _ = self.run_adb(['pull', '/sdcard/temp.png', filename])
            if success2:
                print(f"✓ 截屏保存: {filename}")
                self.run_adb(['shell', 'rm', '/sdcard/temp.png'])
                return True
        return False
    
    def get_ui_elements(self):
        """获取页面元素"""
        # 获取UI结构
        success, _, _ = self.run_adb(['shell', 'uiautomator', 'dump', '/sdcard/ui_dump.xml'])
        if not success:
            return []
        
        # 下载并解析
        success, _, _ = self.run_adb(['pull', '/sdcard/ui_dump.xml', 'temp_ui.xml'])
        if not success:
            return []
        
        elements = []
        try:
            with open('temp_ui.xml', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取节点信息
            pattern = r'<node[^>]*>'
            matches = re.findall(pattern, content)
            
            for match in matches:
                element_info = {}
                attrs = re.findall(r'(\w+)="([^"]*)"', match)
                for attr_name, attr_value in attrs:
                    element_info[attr_name] = attr_value
                
                # 只保留有用的元素
                if (element_info.get('clickable') == 'true' or 
                    element_info.get('text', '').strip() or 
                    element_info.get('content-desc', '').strip()):
                    
                    # 解析坐标
                    bounds = element_info.get('bounds', '')
                    if bounds and '[' in bounds:
                        coords = re.findall(r'\[(\d+),(\d+)\]', bounds)
                        if len(coords) == 2:
                            x1, y1 = int(coords[0][0]), int(coords[0][1])
                            x2, y2 = int(coords[1][0]), int(coords[1][1])
                            element_info['center_x'] = (x1 + x2) // 2
                            element_info['center_y'] = (y1 + y2) // 2
                            element_info['width'] = x2 - x1
                            element_info['height'] = y2 - y1
                            elements.append(element_info)
            
            # 清理临时文件
            os.remove('temp_ui.xml')
            self.run_adb(['shell', 'rm', '/sdcard/ui_dump.xml'])
            
        except Exception as e:
            print(f"解析UI失败: {e}")
        
        return elements
    
    def find_element_by_text(self, text):
        """根据文本查找元素"""
        elements = self.get_ui_elements()
        
        for element in elements:
            element_text = element.get('text', '') + ' ' + element.get('content-desc', '')
            if text.lower() in element_text.lower():
                return element
        return None
    
    def find_elements_by_text(self, text):
        """根据文本查找所有匹配的元素"""
        elements = self.get_ui_elements()
        matches = []
        
        for element in elements:
            element_text = element.get('text', '') + ' ' + element.get('content-desc', '')
            if text.lower() in element_text.lower():
                matches.append(element)
        
        return matches
    
    def click_by_text(self, text):
        """根据文本点击元素"""
        element = self.find_element_by_text(text)
        if element and 'center_x' in element:
            return self.tap(element['center_x'], element['center_y'])
        else:
            print(f"未找到包含文字 '{text}' 的元素")
            return False
    
    def wait_for_element(self, text, timeout=10):
        """等待元素出现"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            element = self.find_element_by_text(text)
            if element:
                return element
            time.sleep(1)
        return None
    
    def show_all_clickable(self):
        """显示所有可点击元素"""
        elements = self.get_ui_elements()
        clickable = [e for e in elements if e.get('clickable') == 'true']
        
        print(f"\n可点击元素 ({len(clickable)} 个):")
        print("-" * 60)
        
        for i, element in enumerate(clickable):
            text = element.get('text', '').strip()
            desc = element.get('content-desc', '').strip()
            display_text = text or desc or f"[{element.get('class', 'Unknown')}]"
            
            print(f"{i+1:2d}. ({element['center_x']:4d},{element['center_y']:4d}) {display_text[:40]}")
        
        self.last_elements = clickable
        return clickable
    
    def click_element_by_index(self, index):
        """根据索引点击元素"""
        if 0 <= index < len(self.last_elements):
            element = self.last_elements[index]
            text = element.get('text', '') or element.get('content-desc', '') or "未知元素"
            print(f"点击第{index+1}个元素: {text}")
            return self.tap(element['center_x'], element['center_y'])
        else:
            print("元素索引超出范围")
            return False

# 快捷使用示例
def demo():
    controller = SmartController()
    
    print("=== 智能手机控制器演示 ===")
    
    # 1. 截屏
    print("1. 截屏...")
    controller.screenshot()
    
    # 2. 显示所有可点击元素
    print("2. 扫描可点击元素...")
    controller.show_all_clickable()
    
    # 3. 交互式选择
    while True:
        choice = input("\n请输入操作 (数字点击元素 / 'text:关键词'搜索 / 'q'退出): ").strip()
        
        if choice.lower() == 'q':
            break
        elif choice.isdigit():
            controller.click_element_by_index(int(choice) - 1)
        elif choice.startswith('text:'):
            keyword = choice[5:]
            matches = controller.find_elements_by_text(keyword)
            if matches:
                print(f"找到 {len(matches)} 个匹配元素:")
                for i, elem in enumerate(matches):
                    text = elem.get('text', '') or elem.get('content-desc', '')
                    print(f"{i+1}. {text}")
                    
                idx = input("选择元素编号: ")
                if idx.isdigit() and 0 < int(idx) <= len(matches):
                    elem = matches[int(idx)-1]
                    controller.tap(elem['center_x'], elem['center_y'])
            else:
                print("未找到匹配元素")
        else:
            print("请输入有效选项")

if __name__ == "__main__":
    demo()