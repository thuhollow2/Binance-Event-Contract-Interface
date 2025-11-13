#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步WebSocket版本的币安监听器（参考工作文件）
"""

import asyncio
import websockets
import json
import subprocess
import os
from datetime import datetime

class AsyncBinanceClicker:
    def __init__(self, device_id="40f06c22", threshold=102826, click_interval=5):
        self.device_id = device_id
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        self.threshold = threshold
        self.click_interval = click_interval
        self.click_coords = (416, 2452)  # 上涨按钮坐标
        
        # 状态控制
        self.is_running = True
        self.last_click_time = 0
        self.total_clicks = 0
        
    def run_adb(self, command):
        """执行ADB命令"""
        try:
            full_cmd = [self.adb_path, '-s', self.device_id] + command
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def click_phone(self):
        """点击手机屏幕"""
        x, y = self.click_coords
        success, _, stderr = self.run_adb(['shell', 'input', 'tap', str(x), str(y)])
        
        current_time = datetime.now().strftime("%H:%M:%S")
        if success:
            self.total_clicks += 1
            self.last_click_time = asyncio.get_event_loop().time()
            print(f"[{current_time}] ✅ 点击成功 #{self.total_clicks} - 坐标({x},{y})")
            return True
        else:
            print(f"[{current_time}] ❌ 点击失败: {stderr}")
            return False
    
    def should_click(self, current_price):
        """判断是否应该点击"""
        if current_price <= self.threshold:
            return False
            
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_click_time < self.click_interval:
            return False
            
        return True
    
    async def run_websocket(self):
        """运行WebSocket监听"""
        ws_url = "wss://stream.binance.com/ws/btcusdt@kline_10m"
        
        print("🚀 启动异步WebSocket监听器")
        print(f"📊 监听: BTCUSDT 10分钟K线")
        print(f"🎯 触发条件: 价格 > {self.threshold}")
        print(f"📱 点击坐标: {self.click_coords}")
        print(f"⏱️  点击间隔: {self.click_interval} 秒")
        print("-" * 60)
        
        while self.is_running:
            try:
                async with websockets.connect(ws_url) as websocket:
                    print(f"✅ WebSocket连接成功: {ws_url}")
                    
                    while self.is_running:
                        try:
                            message = await websocket.recv()
                            data = json.loads(message)
                            
                            # 调试：打印接收到的数据
                            if len(str(data)) > 100:  # 避免打印过长数据
                                print(f"📊 收到数据: {str(data)[:100]}...")
                            else:
                                print(f"📊 收到数据: {data}")
                            
                            # 解析K线数据
                            if 'k' in data:
                                kline = data['k']
                                close_price = float(kline['c'])  # 收盘价
                                high_price = float(kline['h'])   # 最高价
                                low_price = float(kline['l'])    # 最低价
                                
                                # 显示价格信息
                                current_time = datetime.now().strftime("%H:%M:%S")
                                status = "🔥 触发" if close_price > self.threshold else "⏳ 待机"
                                
                                print(f"[{current_time}] {status} BTCUSDT: {close_price:.2f} "
                                      f"(H:{high_price:.2f} L:{low_price:.2f}) "
                                      f"阈值:{self.threshold}")
                                
                                # 检查是否需要点击
                                if self.should_click(close_price):
                                    self.click_phone()
                                elif close_price > self.threshold:
                                    current_loop_time = asyncio.get_event_loop().time()
                                    remaining = self.click_interval - (current_loop_time - self.last_click_time)
                                    print(f"    💤 冷却中，还需等待 {remaining:.1f} 秒")
                                    
                        except websockets.exceptions.ConnectionClosed:
                            print("⚠ WebSocket连接断开")
                            break
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"⚠ 处理消息时出错: {e}")
                            continue
                            
            except websockets.exceptions.WebSocketException as e:
                print(f"⚠ WebSocket异常: {e}")
            except Exception as e:
                print(f"⚠ 连接异常: {e}")
            
            if self.is_running:
                print("🔄 3秒后重新连接...")
                await asyncio.sleep(3)
    
    def stop(self):
        """停止监听"""
        print("\n🛑 正在停止监听...")
        self.is_running = False
        print(f"📊 总点击次数: {self.total_clicks}")
        print("🏁 异步监听器已停止")

async def main():
    print("🎯 异步WebSocket币安监听器")
    print("=" * 50)
    
    clicker = AsyncBinanceClicker(threshold=102826, click_interval=5)
    
    try:
        await clicker.run_websocket()
    except KeyboardInterrupt:
        clicker.stop()
        print("\n用户中断，程序退出")

if __name__ == "__main__":
    asyncio.run(main())