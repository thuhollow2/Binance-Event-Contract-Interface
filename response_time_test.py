#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点击响应时间测试器
测量从发送点击命令到屏幕反应的延迟时间
"""

import subprocess
import os
import time
import json
from datetime import datetime

class ResponseTimeTest:
    def __init__(self, device_id="40f06c22"):
        self.device_id = device_id
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        self.test_results = []
        
    def run_adb(self, command):
        """执行ADB命令并记录时间"""
        try:
            start_time = time.time()
            full_cmd = [self.adb_path, '-s', self.device_id] + command
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=15)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            return result.returncode == 0, result.stdout, result.stderr, execution_time
        except Exception as e:
            return False, "", str(e), 0
    
    def tap_with_timing(self, x, y, test_name=""):
        """带时间记录的点击测试"""
        print(f"\n🎯 测试点击: {test_name} 坐标({x}, {y})")
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行点击
        success, stdout, stderr, cmd_time = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
        
        # 记录结束时间
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        
        result = {
            'test_name': test_name,
            'coordinates': (x, y),
            'success': success,
            'command_time': round(cmd_time, 2),
            'total_time': round(total_time, 2),
            'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3]
        }
        
        if success:
            print(f"✓ 点击成功")
            print(f"  ⏱️  ADB命令执行: {cmd_time:.1f}ms")
            print(f"  ⏱️  总响应时间: {total_time:.1f}ms")
        else:
            print(f"✗ 点击失败: {stderr}")
            
        self.test_results.append(result)
        return success, result
    
    def screenshot_with_timing(self, filename="test_screenshot.png"):
        """带时间记录的截屏"""
        print(f"\n📸 截屏测试: {filename}")
        
        start_time = time.time()
        
        # 截屏到设备
        success1, _, _, cmd1_time = self.run_adb(['shell', 'screencap', '/sdcard/temp_test.png'])
        
        if success1:
            # 下载到电脑
            success2, _, _, cmd2_time = self.run_adb(['pull', '/sdcard/temp_test.png', filename])
            
            if success2:
                # 清理设备文件
                self.run_adb(['shell', 'rm', '/sdcard/temp_test.png'])
                
                end_time = time.time()
                total_time = (end_time - start_time) * 1000
                
                print(f"✓ 截屏成功: {filename}")
                print(f"  ⏱️  设备截屏: {cmd1_time:.1f}ms")
                print(f"  ⏱️  文件传输: {cmd2_time:.1f}ms")
                print(f"  ⏱️  总时间: {total_time:.1f}ms")
                
                return True, total_time
        
        print("✗ 截屏失败")
        return False, 0
    
    def ui_dump_timing(self):
        """测试UI结构获取时间"""
        print(f"\n🔍 UI分析测试")
        
        start_time = time.time()
        
        # UI dump
        success1, _, _, cmd1_time = self.run_adb(['shell', 'uiautomator', 'dump', '/sdcard/ui_test.xml'])
        
        if success1:
            # 下载文件
            success2, _, _, cmd2_time = self.run_adb(['pull', '/sdcard/ui_test.xml', 'ui_timing_test.xml'])
            
            if success2:
                self.run_adb(['shell', 'rm', '/sdcard/ui_test.xml'])
                
                end_time = time.time()
                total_time = (end_time - start_time) * 1000
                
                print(f"✓ UI分析成功")
                print(f"  ⏱️  UI dump: {cmd1_time:.1f}ms")
                print(f"  ⏱️  文件传输: {cmd2_time:.1f}ms")
                print(f"  ⏱️  总时间: {total_time:.1f}ms")
                
                return True, total_time
        
        print("✗ UI分析失败")
        return False, 0
    
    def comprehensive_test(self, test_coordinates=None):
        """综合响应时间测试"""
        if test_coordinates is None:
            # 默认测试坐标 (屏幕中心和四角)
            screen_width, screen_height = 1440, 3200
            test_coordinates = [
                (720, 1600, "屏幕中心"),
                (200, 300, "左上角"),
                (1240, 300, "右上角"),
                (200, 2900, "左下角"),
                (1240, 2900, "右下角"),
                (545, 2025, "输入框"),  # 你之前的输入框坐标
            ]
        
        print("=" * 60)
        print("🚀 开始综合响应时间测试")
        print("=" * 60)
        
        # 1. 截屏测试
        self.screenshot_with_timing("before_test.png")
        
        # 2. UI分析测试
        self.ui_dump_timing()
        
        # 3. 多点点击测试
        for x, y, name in test_coordinates:
            self.tap_with_timing(x, y, name)
            time.sleep(1)  # 间隔1秒避免过快
        
        # 4. 快速连续点击测试
        print(f"\n⚡ 快速连续点击测试")
        rapid_times = []
        for i in range(5):
            start = time.time()
            success, _ = self.tap_with_timing(720, 1600, f"快速点击{i+1}")
            rapid_times.append(time.time() - start)
            time.sleep(0.2)  # 200ms间隔
        
        # 5. 统计分析
        self.analyze_results()
        
        # 6. 最终截屏
        self.screenshot_with_timing("after_test.png")
    
    def analyze_results(self):
        """分析测试结果"""
        if not self.test_results:
            print("❌ 没有测试数据")
            return
        
        print("\n" + "=" * 60)
        print("📊 测试结果统计")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r['success']]
        
        if successful_tests:
            cmd_times = [r['command_time'] for r in successful_tests]
            total_times = [r['total_time'] for r in successful_tests]
            
            print(f"✅ 成功测试: {len(successful_tests)}/{len(self.test_results)}")
            print(f"\n⏱️  ADB命令执行时间:")
            print(f"   平均: {sum(cmd_times)/len(cmd_times):.1f}ms")
            print(f"   最快: {min(cmd_times):.1f}ms")
            print(f"   最慢: {max(cmd_times):.1f}ms")
            
            print(f"\n⏱️  总响应时间:")
            print(f"   平均: {sum(total_times)/len(total_times):.1f}ms")
            print(f"   最快: {min(total_times):.1f}ms")
            print(f"   最慢: {max(total_times):.1f}ms")
            
            print(f"\n📋 详细结果:")
            for r in successful_tests:
                print(f"   {r['test_name']:<12} | ADB: {r['command_time']:>5.1f}ms | 总计: {r['total_time']:>5.1f}ms")
        
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ 失败测试: {len(failed_tests)}")
            for r in failed_tests:
                print(f"   {r['test_name']} - 坐标({r['coordinates']})")
    
    def save_results(self, filename="response_time_results.json"):
        """保存测试结果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 测试结果已保存: {filename}")
    
    def simple_tap_test(self, x=720, y=1600, count=10):
        """简单的连续点击测试"""
        print(f"🎯 简单点击测试 - 坐标({x}, {y}) x{count}次")
        print("-" * 40)
        
        times = []
        for i in range(count):
            start = time.time()
            success, stdout, stderr, cmd_time = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
            end = time.time()
            
            total = (end - start) * 1000
            times.append(total)
            
            status = "✓" if success else "✗"
            print(f"{i+1:2d}. {status} {total:5.1f}ms (ADB: {cmd_time:4.1f}ms)")
            
            time.sleep(0.5)  # 500ms间隔
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n📊 平均响应时间: {avg_time:.1f}ms")
            print(f"   最快: {min(times):.1f}ms")
            print(f"   最慢: {max(times):.1f}ms")

def main():
    tester = ResponseTimeTest()
    
    print("⏱️  手机响应时间测试器")
    print("=" * 40)
    
    while True:
        print("\n选择测试类型:")
        print("1. 简单点击测试 (10次点击屏幕中心)")
        print("2. 综合响应测试 (多种操作)")
        print("3. 自定义坐标点击测试")
        print("4. 只测试截屏时间")
        print("5. 只测试UI分析时间")
        print("q. 退出")
        
        choice = input("\n请选择 (1-5/q): ").strip()
        
        if choice.lower() == 'q':
            break
        elif choice == '1':
            tester.simple_tap_test()
        elif choice == '2':
            tester.comprehensive_test()
            tester.save_results()
        elif choice == '3':
            try:
                x = int(input("输入X坐标: "))
                y = int(input("输入Y坐标: "))
                count = int(input("测试次数 (默认5): ") or "5")
                tester.simple_tap_test(x, y, count)
            except ValueError:
                print("❌ 坐标格式错误")
        elif choice == '4':
            tester.screenshot_with_timing()
        elif choice == '5':
            tester.ui_dump_timing()
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()