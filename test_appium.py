#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Appium连接的简单脚本
"""

import requests
import time

def test_appium_connection():
    """测试Appium服务器连接"""
    try:
        response = requests.get('http://localhost:4723/status', timeout=5)
        if response.status_code == 200:
            print("✓ Appium服务器运行正常")
            return True
        else:
            print(f"✗ Appium服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接Appium服务器")
        print("请在另一个终端窗口中运行: appium")
        return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== Appium连接测试 ===")
    
    if test_appium_connection():
        print("\n现在可以运行: python appium_controller.py")
        
        # 显示设备信息
        print("\n检查设备连接...")
        import subprocess
        import os
        
        adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        try:
            result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                devices = [line for line in lines if line.strip() and 'device' in line]
                if devices:
                    print("✓ 发现以下设备:")
                    for device in devices:
                        print(f"  - {device}")
                else:
                    print("✗ 未发现已连接的设备")
        except Exception as e:
            print(f"✗ 检查设备失败: {e}")
    else:
        print("\n请先启动Appium服务器:")
        print("1. 打开新的PowerShell窗口")
        print("2. 运行命令: appium")
        print("3. 保持该窗口打开")
        print("4. 然后运行此测试脚本")