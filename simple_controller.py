#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的手机控制器 - 只需要手动指定设备ID
"""

from appium_controller import SimpleAppiumController

def main():
    print("=== 简化的币安App控制器 ===")
    print()
    
    # 直接使用检测到的设备ID
    device_id = "40f06c22"  # 你的设备ID
    
    print(f"使用设备ID: {device_id}")
    print("注意: 请确保Appium服务器正在运行")
    print("如果没有运行，请在另一个PowerShell窗口中执行: appium")
    print()
    
    input("准备好后按回车键继续...")
    
    # 创建控制器 (针对Android 15优化)
    controller = SimpleAppiumController(device_name=device_id)
    
    try:
        print("正在连接设备...")
        controller.connect_device()
        
        print("等待币安App启动...")
        controller.sleep(5)
        
        print("截取当前屏幕...")
        controller.take_screenshot("binance_current.png")
        
        print("✓ 连接成功！币安App已启动")
        print("✓ 截屏已保存为: binance_current.png")
        print()
        
        print("现在你可以使用以下命令控制手机:")
        print("controller.tap(x, y)                    # 点击坐标")
        print("controller.swipe(x1, y1, x2, y2)        # 滑动")
        print("controller.click_element('xpath', path)  # 点击元素")
        print("controller.take_screenshot('name.png')  # 截屏")
        print("controller.sleep(seconds)               # 等待")
        print()
        
        # 进入交互模式
        print("进入交互模式，你可以直接输入Python命令:")
        print("例如: controller.tap(500, 1000)")
        print("输入 'quit' 退出")
        print("-" * 50)
        
        while True:
            try:
                command = input(">>> ").strip()
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command:
                    # 执行用户输入的命令
                    exec(command)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"错误: {e}")
        
    except Exception as e:
        print(f"连接失败: {e}")
        print()
        print("请确保:")
        print("1. 在另一个窗口运行了: appium")
        print("2. 手机已连接并开启USB调试")
        print("3. 币安App已安装")
    
    finally:
        print("\n正在断开连接...")
        controller.close()
        print("✓ 已断开连接")

if __name__ == "__main__":
    main()