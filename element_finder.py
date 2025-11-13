#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面元素探测器
帮助查找页面元素的坐标和信息
"""

import subprocess
import os
import json
import re

class ElementFinder:
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
        success, stdout, stderr = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
        if success:
            print(f"✓ 点击坐标: ({x}, {y})")
            return True
        else:
            print(f"✗ 点击失败，尝试其他方法...")
            # 如果权限不足，给出提示
            if "SecurityException" in stderr or "INJECT_EVENTS" in stderr:
                print("提示：如果点击不生效，请在开发者选项中启用'指针位置'和'显示触摸操作'")
            return False
    
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
    
    def dump_ui_hierarchy(self, filename="ui_dump.xml"):
        """获取UI层次结构"""
        print("正在分析页面结构...")
        
        # 使用uiautomator dump命令
        success, stdout, stderr = self.run_adb(['shell', 'uiautomator', 'dump', '/sdcard/ui_dump.xml'])
        
        if success:
            # 下载XML文件
            success2, _, _ = self.run_adb(['pull', '/sdcard/ui_dump.xml', filename])
            if success2:
                print(f"✓ UI结构已保存: {filename}")
                self.run_adb(['shell', 'rm', '/sdcard/ui_dump.xml'])
                return True
        
        print(f"✗ 获取UI结构失败: {stderr}")
        return False
    
    def parse_ui_elements(self, xml_file="ui_dump.xml"):
        """解析UI元素"""
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取所有可点击的元素
            elements = []
            
            # 使用正则表达式查找节点
            pattern = r'<node[^>]*>'
            matches = re.findall(pattern, content)
            
            for match in matches:
                element_info = {}
                
                # 提取属性
                attrs = re.findall(r'(\w+)="([^"]*)"', match)
                for attr_name, attr_value in attrs:
                    element_info[attr_name] = attr_value
                
                # 保留可交互的元素（扩展检测范围）
                if (element_info.get('clickable') == 'true' or 
                    element_info.get('text', '').strip() or 
                    element_info.get('content-desc', '').strip() or
                    'Button' in element_info.get('class', '') or
                    'ImageView' in element_info.get('class', '') or
                    'TextView' in element_info.get('class', '') or
                    element_info.get('focusable') == 'true' or
                    element_info.get('long-clickable') == 'true'):
                    
                    # 解析坐标
                    bounds = element_info.get('bounds', '')
                    if bounds and '[' in bounds:
                        try:
                            # bounds格式: [x1,y1][x2,y2]
                            coords = re.findall(r'\[(\d+),(\d+)\]', bounds)
                            if len(coords) == 2:
                                x1, y1 = int(coords[0][0]), int(coords[0][1])
                                x2, y2 = int(coords[1][0]), int(coords[1][1])
                                center_x = (x1 + x2) // 2
                                center_y = (y1 + y2) // 2
                                element_info['center_x'] = center_x
                                element_info['center_y'] = center_y
                                element_info['width'] = x2 - x1
                                element_info['height'] = y2 - y1
                        except:
                            continue
                    
                    if 'center_x' in element_info:
                        elements.append(element_info)
            
            return elements
            
        except Exception as e:
            print(f"解析UI元素失败: {e}")
            return []
    
    def find_elements_by_text(self, text_keyword):
        """通过文本查找元素"""
        if not self.dump_ui_hierarchy():
            return []
        
        elements = self.parse_ui_elements()
        matching_elements = []
        
        for element in elements:
            element_text = element.get('text', '') + ' ' + element.get('content-desc', '')
            if text_keyword.lower() in element_text.lower():
                matching_elements.append(element)
        
        return matching_elements
    
    def find_element_by_id(self, resource_id):
        """通过resource-id查找元素（类似Web的getElementById）"""
        if not self.dump_ui_hierarchy():
            return None
        
        elements = self.parse_ui_elements()
        for element in elements:
            if element.get('resource-id', '') == resource_id:
                return element
        return None
    
    def find_elements_by_class(self, class_name):
        """通过class名称查找元素（类似Web的getElementsByClassName）"""
        if not self.dump_ui_hierarchy():
            return []
        
        elements = self.parse_ui_elements()
        matching_elements = []
        
        for element in elements:
            element_class = element.get('class', '')
            if class_name.lower() in element_class.lower():
                matching_elements.append(element)
        
        return matching_elements
    
    def find_elements_by_attribute(self, attr_name, attr_value):
        """通过属性查找元素"""
        if not self.dump_ui_hierarchy():
            return []
        
        elements = self.parse_ui_elements()
        matching_elements = []
        
        for element in elements:
            if element.get(attr_name, '') == attr_value:
                matching_elements.append(element)
        
        return matching_elements
    
    def click_by_id(self, resource_id):
        """通过ID点击元素"""
        element = self.find_element_by_id(resource_id)
        if element and 'center_x' in element:
            print(f"通过ID点击: {resource_id}")
            return self.tap(element['center_x'], element['center_y'])
        else:
            print(f"未找到ID为 '{resource_id}' 的元素")
            return False
    
    def click_by_class(self, class_name, index=0):
        """通过class名称点击元素"""
        elements = self.find_elements_by_class(class_name)
        if elements and index < len(elements):
            element = elements[index]
            print(f"通过Class点击: {class_name} (第{index+1}个)")
            return self.tap(element['center_x'], element['center_y'])
        else:
            print(f"未找到class为 '{class_name}' 的元素")
            return False
    
    def click_by_text(self, text, index=0):
        """通过文本点击元素 (可指定第几个)"""
        elements = self.find_elements_by_text(text)
        if elements and index < len(elements):
            element = elements[index]
            element_text = element.get('text', '') or element.get('content-desc', '')
            print(f"通过文本点击: '{text}' (第{index+1}个) -> '{element_text}'")
            return self.tap(element['center_x'], element['center_y'])
        else:
            print(f"未找到包含文本 '{text}' 的第{index+1}个元素")
            return False
    
    def show_clickable_elements(self, limit=20):
        """显示所有可交互的元素"""
        if not self.dump_ui_hierarchy():
            return
        
        elements = self.parse_ui_elements()
        # 扩展可交互元素的定义
        clickable_elements = [e for e in elements if (
            e.get('clickable') == 'true' or
            'Button' in e.get('class', '') or
            'ImageView' in e.get('class', '') or
            e.get('focusable') == 'true'
        )]
        
        print(f"\n找到 {len(clickable_elements)} 个可交互元素:")
        print("-" * 80)
        
        for i, element in enumerate(clickable_elements[:limit]):
            text = element.get('text', '').strip()
            desc = element.get('content-desc', '').strip()
            class_name = element.get('class', '')
            resource_id = element.get('resource-id', '')
            clickable = element.get('clickable', 'false')
            focusable = element.get('focusable', 'false')
            
            display_text = text or desc or f"({class_name})"
            
            # 显示更多属性信息
            attrs = []
            if clickable == 'true':
                attrs.append('可点击')
            if focusable == 'true':
                attrs.append('可聚焦')
            if 'Button' in class_name:
                attrs.append('按钮')
            attr_str = f"[{','.join(attrs)}]" if attrs else ''
            
            # 显示完整的ID信息
            id_display = resource_id if resource_id else '[无ID]'
            class_short = class_name.split('.')[-1] if class_name else '[无类型]'
            
            print(f"{i+1:2d}. 坐标:({element['center_x']:4d},{element['center_y']:4d}) "
                  f"文本:'{display_text[:20]}' {attr_str}")
            print(f"     类型:{class_short} ID:{id_display}")
        
        if len(clickable_elements) > limit:
            print(f"\n--- 显示前{limit}个元素，共{len(clickable_elements)}个 ---")
        else:
            print(f"\n--- 共找到{len(clickable_elements)}个可交互元素 ---")
        
        return clickable_elements[:limit]
    
    def show_all_elements(self, limit=30):
        """显示所有元素（包括不可交互的）"""
        if not self.dump_ui_hierarchy():
            return
        
        elements = self.parse_ui_elements()
        
        print(f"\n找到 {len(elements)} 个元素（所有类型）:")
        print("-" * 80)
        
        for i, element in enumerate(elements[:limit]):
            text = element.get('text', '').strip()
            desc = element.get('content-desc', '').strip()
            class_name = element.get('class', '')
            resource_id = element.get('resource-id', '')
            clickable = element.get('clickable', 'false')
            
            display_text = text or desc or f"({class_name.split('.')[-1]})"
            
            # 标识元素类型
            type_info = []
            if clickable == 'true':
                type_info.append('可点击')
            if 'Button' in class_name:
                type_info.append('按钮')
            if 'EditText' in class_name:
                type_info.append('输入框')
            if 'TextView' in class_name:
                type_info.append('文本')
            if 'ImageView' in class_name:
                type_info.append('图片')
            if 'LinearLayout' in class_name or 'FrameLayout' in class_name:
                type_info.append('布局')
                
            type_str = f"[{','.join(type_info)}]" if type_info else '[未知]'
            
            print(f"{i+1:2d}. 坐标:({element['center_x']:4d},{element['center_y']:4d}) "
                  f"文本:'{display_text[:20]}' {type_str}")
        
        if len(elements) > limit:
            print(f"\n--- 显示前{limit}个元素，共{len(elements)}个 ---")
        else:
            print(f"\n--- 共找到{len(elements)}个元素 ---")
        
        return elements[:limit]
    
    def type_text(self, text):
        """输入文字"""
        escaped_text = text.replace(' ', '%s').replace('&', '\\&')
        success, _, stderr = self.run_adb(['shell', 'input', 'text', escaped_text])
        if success:
            print(f"✓ 输入文字: {text}")
            return True
        else:
            print(f"✗ 输入失败: {stderr}")
            return False
    
    def hide_keyboard(self):
        """关闭键盘"""
        # 方法1: 按返回键
        success, _, _ = self.run_adb(['shell', 'input', 'keyevent', '4'])
        if success:
            print("✓ 键盘已关闭 (返回键)")
            return True
        
        # 方法2: 点击空白区域
        success2, _, _ = self.run_adb(['shell', 'input', 'tap', '720', '1000'])
        if success2:
            print("✓ 键盘已关闭 (点击空白)")
            return True
        
        return False
    
    def press_key(self, key_code):
        """按键 (例如: KEYCODE_BACK=4, KEYCODE_HOME=3, KEYCODE_ENTER=66)"""
        success, _, _ = self.run_adb(['shell', 'input', 'keyevent', str(key_code)])
        if success:
            print(f"✓ 按键: {key_code}")
        return success
    
    def interactive_mode(self):
        """交互式元素查找模式"""
        print("=== 页面元素探测器 ===")
        print("帮助你找到页面元素的坐标和信息")
        
        while True:
            print("\n可用命令:")
            print("scan - 扫描当前页面的可交互元素")
            print("all - 显示所有元素（包括不可点击的）")
            print("full - 显示完整的可交互元素列表（无限制）")
            print("find '关键词' - 查找包含关键词的元素")
            print("click 数字 - 点击扫描结果中的第N个元素")
            print("tap(x, y) - 直接点击坐标")
            print("id 'resource-id' - 通过ID查找元素")
            print("class 'class名' - 通过class查找元素") 
            print("clickid 'id' - 通过ID点击元素")
            print("clickclass 'class' - 通过class点击元素")
            print("clicktext 'text' [数字] - 通过文本点击元素")
            print("type 'text' - 输入文字")
            print("hide - 关闭键盘")
            print("enter - 按回车键")
            print("back - 按返回键")
            print("screenshot - 截屏")
            print("quit - 退出")
            
            cmd = input("\n元素探测器 >>> ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                break
            elif cmd == 'scan':
                self.last_elements = self.show_clickable_elements(limit=100)
            elif cmd == 'all':
                self.last_elements = self.show_all_elements(limit=100)
            elif cmd == 'full':
                self.last_elements = self.show_clickable_elements(limit=999)
            elif cmd.startswith('find '):
                keyword = cmd[5:].strip().strip('"\'')
                if keyword:
                    elements = self.find_elements_by_text(keyword)
                    if elements:
                        print(f"\n找到 {len(elements)} 个包含 '{keyword}' 的元素:")
                        for i, element in enumerate(elements[:10]):
                            text = element.get('text', '') or element.get('content-desc', '')
                            print(f"{i+1}. 坐标:({element['center_x']},{element['center_y']}) 文本:'{text}'")
                        self.last_elements = elements[:10]
                    else:
                        print(f"未找到包含 '{keyword}' 的元素")
            elif cmd.startswith('click '):
                try:
                    index = int(cmd[6:]) - 1
                    if hasattr(self, 'last_elements') and 0 <= index < len(self.last_elements):
                        element = self.last_elements[index]
                        x, y = element['center_x'], element['center_y']
                        text = element.get('text', '') or element.get('content-desc', '')
                        print(f"点击元素: '{text}' 坐标:({x},{y})")
                        self.tap(x, y)
                    else:
                        print("元素编号无效，请先使用 scan 或 find 命令")
                except ValueError:
                    print("请输入有效的数字")
            elif cmd.startswith('tap(') and cmd.endswith(')'):
                try:
                    coords = cmd[4:-1].split(',')
                    if len(coords) == 2:
                        x, y = int(coords[0].strip()), int(coords[1].strip())
                        self.tap(x, y)
                except ValueError:
                    print("坐标格式错误")
            elif cmd.startswith('id '):
                resource_id = cmd[3:].strip().strip('"\'')
                if resource_id:
                    element = self.find_element_by_id(resource_id)
                    if element:
                        print(f"找到ID元素: {resource_id}")
                        print(f"  坐标: ({element['center_x']}, {element['center_y']})")
                        print(f"  类型: {element.get('class', '')}")
                        print(f"  文本: {element.get('text', '') or element.get('content-desc', '')}")
                    else:
                        print(f"未找到ID: {resource_id}")
            elif cmd.startswith('class '):
                class_name = cmd[6:].strip().strip('"\'')
                if class_name:
                    elements = self.find_elements_by_class(class_name)
                    if elements:
                        print(f"找到 {len(elements)} 个class包含 '{class_name}' 的元素:")
                        for i, element in enumerate(elements[:10]):
                            text = element.get('text', '') or element.get('content-desc', '') or '[无文本]'
                            print(f"{i+1}. 坐标:({element['center_x']},{element['center_y']}) 文本:'{text}'")
                        self.last_elements = elements[:10]
                    else:
                        print(f"未找到class: {class_name}")
            elif cmd.startswith('clickid '):
                resource_id = cmd[8:].strip().strip('"\'')
                if resource_id:
                    self.click_by_id(resource_id)
            elif cmd.startswith('clickclass '):
                class_name = cmd[11:].strip().strip('"\'')
                if class_name:
                    self.click_by_class(class_name)
            elif cmd.startswith('clicktext '):
                parts = cmd[10:].strip().split()
                if parts:
                    text = parts[0].strip('"\'')
                    index = int(parts[1]) - 1 if len(parts) > 1 and parts[1].isdigit() else 0
                    self.click_by_text(text, index)
            elif cmd.startswith('type '):
                text = cmd[5:].strip().strip('"\'')
                if text:
                    self.type_text(text)
                else:
                    print("请输入要输入的文字")
            elif cmd == 'hide':
                self.hide_keyboard()
            elif cmd == 'enter':
                self.press_key(66)  # KEYCODE_ENTER
            elif cmd == 'back':
                self.press_key(4)   # KEYCODE_BACK
            elif cmd == 'screenshot':
                self.screenshot()
            elif cmd == 'help':
                print("📱 元素选择方法:")
                print("1️⃣ 坐标方式: click 1, tap(x,y)")
                print("2️⃣ ID方式: id 'com.example:id/button', clickid 'resource-id'")
                print("3️⃣ 类型方式: class 'Button', clickclass 'ImageButton'")
                print("4️⃣ 文本方式: find '买入', clicktext '上涨' 2 (点击第2个)")
                print("5️⃣ 精确选择: clicktext '上涨' 1 或 clicktext '上涨' 2")
                print("")
                print("🎯 完整操作流程:")
                print("1. scan - 扫描页面元素")
                print("2. click 1 或 clickid 'button_id' - 点击元素")
                print("3. type '123' - 输入数字")
                print("4. hide 或 enter - 关闭键盘/确认")
                print("")
                print("💡 提示: Android元素通常有resource-id属性，类似Web的id")
            elif cmd:
                print("未知命令，输入 help 查看帮助")

def main():
    finder = ElementFinder()
    finder.interactive_mode()

if __name__ == "__main__":
    main()