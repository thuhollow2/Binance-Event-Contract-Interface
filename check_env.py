#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Android环境设置
"""

import os
import subprocess

def check_environment():
    print("=== Android环境检查 ===")
    print()
    
    # 检查环境变量
    android_home = os.environ.get('ANDROID_HOME')
    android_sdk_root = os.environ.get('ANDROID_SDK_ROOT')
    
    print("环境变量检查:")
    if android_home:
        print(f"✓ ANDROID_HOME = {android_home}")
    else:
        print("✗ ANDROID_HOME 未设置")
        return False
    
    if android_sdk_root:
        print(f"✓ ANDROID_SDK_ROOT = {android_sdk_root}")
    else:
        print("✗ ANDROID_SDK_ROOT 未设置")
        return False
    
    print()
    
    # 检查ADB
    try:
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ ADB 可用")
            print(f"  版本: {result.stdout.split()[4]}")
        else:
            print("✗ ADB 不可用")
            return False
    except FileNotFoundError:
        print("✗ ADB 未找到")
        return False
    except Exception as e:
        print(f"✗ ADB 检查失败: {e}")
        return False
    
    # 检查设备连接
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split('\n')[1:]
        devices = [line for line in lines if line.strip() and 'device' in line]
        
        if devices:
            print(f"✓ 发现 {len(devices)} 个设备:")
            for device in devices:
                print(f"  - {device}")
        else:
            print("⚠ 未发现设备连接")
    except Exception as e:
        print(f"✗ 设备检查失败: {e}")
    
    print()
    return True

def check_appium():
    print("=== Appium检查 ===")
    
    # 检查Appium是否可用
    try:
        result = subprocess.run(['appium', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Appium 版本: {result.stdout.strip()}")
        else:
            print("✗ Appium 不可用")
            return False
    except FileNotFoundError:
        print("✗ Appium 未安装")
        return False
    
    # 检查Appium服务器状态
    import requests
    try:
        response = requests.get('http://localhost:4723/status', timeout=5)
        if response.status_code == 200:
            print("✓ Appium服务器运行中")
        else:
            print("✗ Appium服务器未运行")
            print("  请在另一个窗口运行: appium")
    except requests.exceptions.ConnectionError:
        print("✗ Appium服务器未运行")
        print("  请在另一个窗口运行: appium")
    except Exception as e:
        print(f"✗ Appium服务器检查失败: {e}")
    
    print()
    return True

def main():
    print("币安App自动化环境验证")
    print("=" * 40)
    print()
    
    env_ok = check_environment()
    appium_ok = check_appium()
    
    print("=" * 40)
    if env_ok and appium_ok:
        print("🎉 环境配置完成！")
        print()
        print("下一步:")
        print("1. 如果Appium服务器未运行，请在新窗口执行: appium")
        print("2. 然后运行: python simple_controller.py")
    else:
        print("⚠️  环境配置有问题，请检查上述错误")
        print()
        print("如果是第一次运行，请:")
        print("1. 关闭所有PowerShell窗口")
        print("2. 重新打开PowerShell")
        print("3. 重新运行此检查脚本")

if __name__ == "__main__":
    main()