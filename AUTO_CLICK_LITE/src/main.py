#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连点器(Auto-Clicker)主程序
"""
import os
import sys
import json
import threading
import time
from pathlib import Path

# 导入自定义模块
import importlib
import clicker
importlib.reload(clicker)
from clicker import Clicker
from config import Config
from hotkey import HotkeyListener
from gui import GUI

class AutoClickerApp:
    def __init__(self):
        # 初始化配置
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        self.config = Config(config_path)
        self.settings = self.config.load_config()
        
        # 初始化点击器
        self.clicker = Clicker(
            interval=self.settings['default_settings']['interval'],
            count=self.settings['default_settings']['count'],
            button=self.settings['default_settings']['button'],
            randomize=self.settings['default_settings']['randomize'],
            min_interval=self.settings['default_settings']['min_interval'],
            max_interval=self.settings['default_settings']['max_interval'],
            position_type=self.settings['default_settings']['position_type'],
            fixed_position=self.settings['default_settings']['fixed_position'],
            multi_position=self.settings['default_settings']['multi_position'],
            positions=self.settings['default_settings']['positions']
        )
        
        # 初始化热键监听器
        self.hotkey_listener = HotkeyListener(
            start_hotkey=self.settings['default_settings']['hotkeys']['start'],
            stop_hotkey=self.settings['default_settings']['hotkeys']['stop'],
            pause_hotkey=self.settings['default_settings']['hotkeys']['pause'],
            on_start=self.start_clicking,
            on_stop=self.stop_clicking,
            on_pause=self.pause_clicking
        )
        
        # 初始化GUI
        self.gui = GUI(
            settings=self.settings,
            on_start=self.start_clicking,
            on_stop=self.stop_clicking,
            on_pause=self.pause_clicking,
            on_settings_change=self.update_settings
        )
        
        # 运行状态标志
        self.running = False
        self.paused = False
        self.click_thread = None

    def start_clicking(self):
        """开始点击"""
        if not self.running and not self.paused:
            self.running = True
            self.paused = False
            self.click_thread = threading.Thread(target=self.clicker.start_clicking, daemon=True)
            self.click_thread.start()
            self.gui.update_status("运行中")
        elif self.paused:
            self.paused = False
            self.clicker.resume_clicking()
            self.gui.update_status("运行中")

    def stop_clicking(self):
        """停止点击"""
        if self.running:
            self.running = False
            self.paused = False
            self.clicker.stop_clicking()
            if self.click_thread and self.click_thread.is_alive():
                self.click_thread.join(timeout=1.0)
            self.gui.update_status("已停止")

    def pause_clicking(self):
        """暂停/恢复点击"""
        if self.running:
            if not self.paused:
                self.paused = True
                self.clicker.pause_clicking()
                self.gui.update_status("已暂停")
            else:
                self.paused = False
                self.clicker.resume_clicking()
                self.gui.update_status("运行中")

    def update_settings(self, new_settings):
        """更新设置"""
        self.settings = new_settings
        self.config.save_config(self.settings)

        # 更新点击器设置
        self.clicker.update_settings(
            interval=self.settings['default_settings']['interval'],
            count=self.settings['default_settings']['count'],
            button=self.settings['default_settings']['button'],
            randomize=self.settings['default_settings']['randomize'],
            min_interval=self.settings['default_settings']['min_interval'],
            max_interval=self.settings['default_settings']['max_interval'],
            position_type=self.settings['default_settings']['position_type'],
            fixed_position=self.settings['default_settings']['fixed_position'],
            multi_position=self.settings['default_settings']['multi_position'],
            positions=self.settings['default_settings']['positions']
        )
        self.clicker.update_settings(
            interval=self.settings['default_settings']['interval'],
            count=self.settings['default_settings']['count'],
            button=self.settings['default_settings']['button'],
            randomize=self.settings['default_settings']['randomize'],
            min_interval=self.settings['default_settings']['min_interval'],
            max_interval=self.settings['default_settings']['max_interval'],
            position_type=self.settings['default_settings']['position_type'],
            fixed_position=self.settings['default_settings']['fixed_position']
        )
        self.hotkey_listener.update_hotkeys(
            start_hotkey=self.settings['default_settings']['hotkeys']['start'],
            stop_hotkey=self.settings['default_settings']['hotkeys']['stop'],
            pause_hotkey=self.settings['default_settings']['hotkeys']['pause']
        )

    def run(self):
        """运行应用程序"""
        # 启动热键监听
        self.hotkey_listener.start_listening()
        
        # 启动GUI主循环
        try:
            self.gui.run()
        except Exception as e:
            print(f"GUI运行出错: {e}")
        finally:
            # 确保程序退出时停止所有线程
            self.stop_clicking()
            self.hotkey_listener.stop_listening()

if __name__ == "__main__":
    app = AutoClickerApp()
    app.run()