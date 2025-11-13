#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接启动WebSocket监听 - 简化版
"""

import asyncio
import websockets
import json
import subprocess
import os
import time
from datetime import datetime

class DirectWebSocketClicker:
    def __init__(self):
        self.device_id = "40f06c22"
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        self.threshold = 102826
        self.click_coords = (416, 2452)
        self.click_interval = 5
        self.last_click_time = 0
        self.total_clicks = 0
        
    def click_phone(self, current_price):
        """点击手机"""
        try:
            x, y = self.click_coords
            full_cmd = [self.adb_path, '-s', self.device_id, 'shell', 'input', 'tap', str(x), str(y)]
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
            
            current_time = datetime.now().strftime("%H:%M:%S")
            if result.returncode == 0:
                self.total_clicks += 1
                self.last_click_time = time.time()
                print(f"[{current_time}] ✅ 点击成功 #{self.total_clicks} - 价格:{current_price:.2f} - 坐标({x},{y})")
                return True
            else:
                print(f"[{current_time}] ❌ 点击失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 点击异常: {e}")
            return False
    
    def should_click(self, current_price):
        """判断是否应该点击"""
        if current_price <= self.threshold:
            return False
        
        current_time = time.time()
        if current_time - self.last_click_time < self.click_interval:
            return False
        
        return True
    
    async def process_message(self, message):
        """处理WebSocket消息"""
        try:
            data = json.loads(message)
            
            # 检查是否是K线数据
            if 'k' in data:
                kline = data['k']
                close_price = float(kline['c'])  # 收盘价
                high_price = float(kline['h'])   # 最高价
                low_price = float(kline['l'])    # 最低价
                
                current_time = datetime.now().strftime("%H:%M:%S")
                status = "🔥 触发" if close_price > self.threshold else "⏳ 待机"
                
                print(f"[{current_time}] {status} BTCUSDT: {close_price:.2f} (H:{high_price:.2f} L:{low_price:.2f}) 阈值:{self.threshold}")
                
                # 检查点击条件
                if self.should_click(close_price):
                    self.click_phone(close_price)
                elif close_price > self.threshold:
                    remaining = self.click_interval - (time.time() - self.last_click_time)
                    print(f"    💤 冷却中，还需等待 {remaining:.1f} 秒")
            else:
                print(f"📊 收到非K线数据: {data}")
                
        except json.JSONDecodeError:
            print("⚠ JSON解析失败")
        except Exception as e:
            print(f"⚠ 消息处理错误: {e}")
    
    async def start(self):
        """启动WebSocket连接"""
        ws_url = "wss://fstream.binance.com/ws/btcusdt@kline_1s"
        
        print(f"🔗 连接到: {ws_url}")
        print("🚀 WebSocket连接成功!")
        print(f"📊 监听: BTCUSDT 1秒K线 (实时监控)")
        print(f"🎯 触发条件: 价格 > {self.threshold}")
        print(f"📱 点击坐标: {self.click_coords}")
        print(f"⏱️ 点击间隔: {self.click_interval} 秒")
        print("-" * 60)
        
        while True:
            try:
                async with websockets.connect(ws_url) as ws:
                    print("✅ WebSocket连接建立成功")
                    while True:
                        message = await ws.recv()
                        await self.process_message(message)
            except websockets.exceptions.ConnectionClosed:
                print("⚠ WebSocket连接断开，3秒后重连...")
                await asyncio.sleep(3)
            except Exception as e:
                print(f"⚠ WebSocket异常: {e}")
                await asyncio.sleep(2)

async def main():
    print("🎯 WebSocket币安监听器 - 直启版")
    print("=" * 50)
    print("⚡ 正在启动WebSocket连接...")
    
    clicker = DirectWebSocketClicker()
    
    try:
        await clicker.start()
    except KeyboardInterrupt:
        print(f"\n🛑 用户中断")
        print(f"📊 总点击次数: {clicker.total_clicks}")
        print("🏁 程序已停止")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🏁 程序已停止")