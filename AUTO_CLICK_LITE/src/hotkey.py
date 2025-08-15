#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热键模块 - 处理键盘热键监听
"""
from pynput import keyboard
import threading

class HotkeyListener:
    def __init__(self, start_hotkey='f6', stop_hotkey='f7', pause_hotkey='f8',
                 on_start=None, on_stop=None, on_pause=None):
        """初始化热键监听器
        Args:
            start_hotkey: 启动热键
            stop_hotkey: 停止热键
            pause_hotkey: 暂停/恢复热键
            on_start: 启动回调函数
            on_stop: 停止回调函数
            on_pause: 暂停/恢复回调函数
        """
        self.start_hotkey = start_hotkey.lower()
        self.stop_hotkey = stop_hotkey.lower()
        self.pause_hotkey = pause_hotkey.lower()
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_pause = on_pause
        
        self.listener = None
        self.running = False

    def update_hotkeys(self, start_hotkey=None, stop_hotkey=None, pause_hotkey=None):
        """更新热键设置"""
        if start_hotkey is not None:
            self.start_hotkey = start_hotkey.lower()
        if stop_hotkey is not None:
            self.stop_hotkey = stop_hotkey.lower()
        if pause_hotkey is not None:
            self.pause_hotkey = pause_hotkey.lower()

    def _on_press(self, key):
        """按键按下事件处理"""
        try:
            # 获取按键名称
            key_name = key.char.lower() if hasattr(key, 'char') else key.name.lower()

            # 检查是否是热键
            if key_name == self.start_hotkey and self.on_start:
                self.on_start()
            elif key_name == self.stop_hotkey and self.on_stop:
                self.on_stop()
            elif key_name == self.pause_hotkey and self.on_pause:
                self.on_pause()
        except Exception as e:
            print(f"热键处理出错: {e}")

    def start_listening(self):
        """开始监听热键"""
        if not self.running:
            self.running = True
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()
            # 启动守护线程以保持监听
            self.listener_thread = threading.Thread(target=self._keep_listening, daemon=True)
            self.listener_thread.start()

    def _keep_listening(self):
        """保持监听线程运行"""
        while self.running:
            try:
                # 检查监听器是否还在运行
                if not self.listener.is_alive():
                    self.listener = keyboard.Listener(on_press=self._on_press)
                    self.listener.start()
                # 短暂休眠以减少CPU使用率
                threading.Event().wait(0.5)
            except Exception as e:
                print(f"监听线程出错: {e}")
                break

    def stop_listening(self):
        """停止监听热键"""
        if self.running:
            self.running = False
            if self.listener and self.listener.is_alive():
                self.listener.stop()
                self.listener.join(timeout=1.0)