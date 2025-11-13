#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安WebSocket价格监听器 + 自动点击
监听BTCUSDT 10分钟K线，价格高于102826时自动点击手机
"""

import websocket
import json
import threading
import time
import subprocess
import os
import requests
import asyncio
from datetime import datetime

class BinanceAutoClicker:
    def __init__(self, device_id="40f06c22", threshold=102826, click_interval=5):
        self.device_id = device_id
        self.adb_path = os.path.join(os.getcwd(), 'android-tools', 'platform-tools', 'adb.exe')
        self.threshold = threshold
        self.click_interval = click_interval
        self.click_coords = (416, 2452)  # 上涨按钮坐标
        
        # 状态控制
        self.is_running = True
        self.last_click_time = 0
        self.current_price = 0
        self.ws = None
        
        # 统计信息
        self.total_clicks = 0
        self.start_time = time.time()
        self.connection_attempts = 0
        self.max_attempts = 5
        
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
            self.last_click_time = time.time()
            print(f"[{current_time}] ✅ 点击成功 #{self.total_clicks} - 坐标({x},{y}) - 价格: {self.current_price:.2f}")
            return True
        else:
            print(f"[{current_time}] ❌ 点击失败: {stderr}")
            return False
    
    def should_click(self):
        """判断是否应该点击"""
        if self.current_price <= self.threshold:
            return False
            
        current_time = time.time()
        if current_time - self.last_click_time < self.click_interval:
            return False
            
        return True
    
    def on_message(self, ws, message):
        """WebSocket消息处理"""
        try:
            data = json.loads(message)
            
            # 解析K线数据
            if 'k' in data:
                kline = data['k']
                close_price = float(kline['c'])  # 收盘价
                high_price = float(kline['h'])   # 最高价
                low_price = float(kline['l'])    # 最低价
                volume = float(kline['v'])       # 成交量
                
                self.current_price = close_price
                
                # 显示价格信息
                current_time = datetime.now().strftime("%H:%M:%S")
                status = "🔥 触发" if close_price > self.threshold else "⏳ 待机"
                
                print(f"[{current_time}] {status} BTCUSDT: {close_price:.2f} "
                      f"(H:{high_price:.2f} L:{low_price:.2f}) "
                      f"阈值:{self.threshold}")
                
                # 检查是否需要点击
                if self.should_click():
                    self.click_phone()
                elif close_price > self.threshold:
                    remaining = self.click_interval - (time.time() - self.last_click_time)
                    print(f"    💤 冷却中，还需等待 {remaining:.1f} 秒")
                    
        except Exception as e:
            print(f"❌ 消息处理错误: {e}")
    
    def on_error(self, ws, error):
        """WebSocket错误处理"""
        error_msg = str(error)
        if "10054" in error_msg or "远程主机强迫关闭" in error_msg:
            print(f"⚠️ 网络连接被重置...")
        elif "10060" in error_msg or "超时" in error_msg:
            print(f"⚠️ 连接超时...")
        else:
            # 不输出详细错误，避免干扰
            pass
    
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭处理"""
        if close_status_code:
            print(f"🔌 WebSocket连接关闭 (代码: {close_status_code})")
        else:
            print("🔌 WebSocket连接已关闭")
            
        if self.is_running:
            print("🔄 5秒后重新连接...")
            time.sleep(5)
            # 直接重连，不使用线程
            self.start_monitoring()
    
    def on_open(self, ws):
        """WebSocket连接建立"""
        print("🚀 币安WebSocket连接已建立")
        print(f"📊 监听: BTCUSDT 10分钟K线")
        print(f"🎯 触发条件: 价格 > {self.threshold}")
        print(f"📱 点击坐标: {self.click_coords}")
        print(f"⏱️  点击间隔: {self.click_interval} 秒")
        print("-" * 60)
    
    def start_monitoring(self):
        """开始监听"""
        if not self.is_running:
            return
            
        # 使用币安正确的WebSocket地址（参考工作文件）
        ws_url = "wss://stream.binance.com/ws/btcusdt@kline_10m"
        
        try:
            print(f"🔄 连接币安WebSocket: {ws_url}")
            
            # 设置WebSocket选项（优化参数）
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # 优化连接参数
            self.ws.run_forever(
                ping_interval=20,
                ping_timeout=10
            )
            
        except Exception as e:
            print(f"❌ WebSocket连接失败: {e}")
            print("🔄 切换到REST API模式...")
            self.start_rest_monitoring()
    
    def stop(self):
        """停止监听"""
        print("\n🛑 正在停止监听...")
        self.is_running = False
        if self.ws:
            self.ws.close()
        
        # 显示统计信息
        runtime = time.time() - self.start_time
        print(f"\n📊 运行统计:")
        print(f"   运行时间: {runtime/60:.1f} 分钟")
        print(f"   总点击次数: {self.total_clicks}")
        print(f"   当前价格: {self.current_price:.2f}")
        print("🏁 程序已停止")
    
    def get_price_rest(self):
        """通过REST API获取BTCUSDT价格"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"❌ 获取价格失败: {e}")
            return None
    
    def start_rest_monitoring(self):
        """使用REST API监听模式（备用）"""
        print("📡 启动REST API监听模式（每30秒检查一次）")
        
        while self.is_running:
            try:
                price = self.get_price_rest()
                if price:
                    self.current_price = price
                    current_time = datetime.now().strftime("%H:%M:%S")
                    status = "🔥 触发" if price > self.threshold else "⏳ 待机"
                    
                    print(f"[{current_time}] {status} BTCUSDT: {price:.2f} (阈值:{self.threshold})")
                    
                    if self.should_click():
                        self.click_phone()
                    elif price > self.threshold:
                        remaining = self.click_interval - (time.time() - self.last_click_time)
                        print(f"    💤 冷却中，还需等待 {remaining:.1f} 秒")
                
                # 等待30秒再检查
                time.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ REST监听错误: {e}")
                time.sleep(10)
    
    def test_click(self):
        """测试点击功能"""
        print("🧪 测试点击功能...")
        if self.click_phone():
            print("✅ 点击测试成功！")
        else:
            print("❌ 点击测试失败，请检查ADB连接")
        return True
    
    def test_network(self):
        """测试网络连通性"""
        print("🌐 测试网络连接...")
        try:
            # 测试币安API连通性
            response = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
            if response.status_code == 200:
                print("✅ 币安API连接正常")
                return True
            else:
                print(f"❌ 币安API响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 网络连接失败: {e}")
            return False
    
    def test_price(self):
        """测试价格获取"""
        print("📊 测试价格获取...")
        price = self.get_price_rest()
        if price:
            print(f"✅ 当前BTCUSDT价格: {price:.2f}")
            return True
        else:
            print("❌ 价格获取失败")
            return False

def main():
    print("🎯 币安价格监听自动点击器")
    print("=" * 50)
    
    # 配置参数
    threshold = 102826  # 价格阈值
    click_interval = 5  # 点击间隔（秒）
    
    clicker = BinanceAutoClicker(threshold=threshold, click_interval=click_interval)
    
    # 交互菜单
    while True:
        print("\n📋 操作菜单:")
        print("1. WebSocket监听 (实时K线)")
        print("2. REST API监听 (30秒间隔)")
        print("3. 测试点击功能")
        print("4. 测试价格获取")
        print("5. 测试网络连接")
        print("6. 修改价格阈值")
        print("7. 修改点击间隔")
        print("8. 查看当前配置")
        print("q. 退出程序")
        
        choice = input("\n请选择操作 (1-8/q): ").strip()
        
        if choice.lower() == 'q':
            break
        elif choice == '1':
            print(f"\n🎬 启动WebSocket监听...")
            try:
                clicker.start_monitoring()
            except KeyboardInterrupt:
                clicker.stop()
        elif choice == '2':
            print(f"\n📡 启动REST API监听...")
            try:
                clicker.start_rest_monitoring()
            except KeyboardInterrupt:
                clicker.stop()
        elif choice == '3':
            clicker.test_click()
        elif choice == '4':
            clicker.test_price()
        elif choice == '5':
            clicker.test_network()
        elif choice == '6':
            try:
                new_threshold = float(input(f"输入新的价格阈值 (当前: {clicker.threshold}): "))
                clicker.threshold = new_threshold
                print(f"✅ 价格阈值已更新为: {new_threshold}")
            except ValueError:
                print("❌ 输入格式错误")
        elif choice == '7':
            try:
                new_interval = int(input(f"输入新的点击间隔/秒 (当前: {clicker.click_interval}): "))
                clicker.click_interval = new_interval
                print(f"✅ 点击间隔已更新为: {new_interval} 秒")
            except ValueError:
                print("❌ 输入格式错误")
        elif choice == '8':
            print(f"\n📋 当前配置:")
            print(f"   价格阈值: {clicker.threshold}")
            print(f"   点击间隔: {clicker.click_interval} 秒")
            print(f"   点击坐标: {clicker.click_coords}")
            print(f"   设备ID: {clicker.device_id}")
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()