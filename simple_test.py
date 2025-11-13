#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试版 - 检查价格和点击功能
"""

import requests
import subprocess
import os
import time
from datetime import datetime

class SimpleTest:
    def __init__(self):
        self.device_id = "40f06c22"
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        self.click_coords = (416, 2452)
        
    def get_btc_price(self):
        """获取当前BTC价格"""
        try:
            response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"❌ 获取价格失败: {e}")
            return None
    
    def click_phone(self):
        """点击手机"""
        try:
            x, y = self.click_coords
            full_cmd = [self.adb_path, '-s', self.device_id, 'shell', 'input', 'tap', str(x), str(y)]
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
            
            current_time = datetime.now().strftime("%H:%M:%S")
            if result.returncode == 0:
                print(f"[{current_time}] ✅ 点击成功 - 坐标({x},{y})")
                return True
            else:
                print(f"[{current_time}] ❌ 点击失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 点击异常: {e}")
            return False
    
    def test_run(self, threshold=102826):
        """测试运行"""
        print("🔍 简单测试模式")
        print(f"🎯 阈值: {threshold}")
        print(f"📱 点击坐标: {self.click_coords}")
        print("-" * 50)
        
        for i in range(10):  # 测试10次
            # 1. 获取价格
            price = self.get_btc_price()
            if price is None:
                time.sleep(3)
                continue
            
            # 2. 显示状态
            current_time = datetime.now().strftime("%H:%M:%S")
            if price > threshold:
                print(f"[{current_time}] 🔥 价格 {price:.2f} > {threshold} - 触发点击!")
                self.click_phone()
            else:
                print(f"[{current_time}] ⏳ 价格 {price:.2f} < {threshold} - 待机中...")
            
            # 3. 等待
            print(f"    💤 等待5秒...\n")
            time.sleep(5)
    
    def force_click_test(self):
        """强制点击测试（无论价格）"""
        print("🧪 强制点击测试")
        for i in range(3):
            print(f"第{i+1}次测试点击:")
            success = self.click_phone()
            if success:
                print("✅ 点击测试成功!")
            else:
                print("❌ 点击测试失败!")
            time.sleep(2)

def main():
    tester = SimpleTest()
    
    print("🎯 简单测试工具")
    print("=" * 40)
    
    while True:
        print("\n选择测试:")
        print("1. 检查当前价格")
        print("2. 强制点击测试（3次）")
        print("3. 价格监听测试（10次循环）")
        print("4. 降低阈值测试（阈值=90000）")
        print("q. 退出")
        
        choice = input("\n请选择 (1-4/q): ").strip()
        
        if choice.lower() == 'q':
            break
        elif choice == '1':
            price = tester.get_btc_price()
            if price:
                print(f"📊 当前BTCUSDT价格: {price:.2f}")
            else:
                print("❌ 获取价格失败")
        elif choice == '2':
            tester.force_click_test()
        elif choice == '3':
            print("🔄 开始10次价格监听测试...")
            tester.test_run(threshold=102826)
        elif choice == '4':
            print("🔥 降低阈值到90000进行测试...")
            tester.test_run(threshold=90000)  # 肯定会触发的低阈值
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()