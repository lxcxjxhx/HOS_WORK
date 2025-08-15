#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块 - 处理配置文件的加载和保存
"""
import json
import os

class Config:
    def __init__(self, config_path):
        """初始化配置管理器
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        # 确保配置文件存在
        if not os.path.exists(self.config_path):
            self._create_default_config()

    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "default_settings": {
                "interval": 100,
                "min_interval": 80,
                "max_interval": 120,
                "count": -1,
                "button": "left",
                "click_type": "single",
                "position_type": "current",
                "fixed_position": {"x": 0, "y": 0},
                "hotkeys": {
                    "start": "f6",
                    "stop": "f7",
                    "pause": "f8"
                },
                "randomize": True,
                "sound_effects": False,
                "dark_mode": False,
                "multi_position": False,
                "positions": [
                    {
                        "x": 0,
                        "y": 0,
                        "note": "默认位置",
                        "enabled": True,
                        "text": "",
                        "text_interval": 1000
                    }
                ]
            },
            "app_settings": {
                "language": "zh",
                "check_for_updates": True,
                "logging_enabled": False,
                "log_level": "INFO"
            }
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)

    def load_config(self):
        """加载配置文件
        Returns:
            配置字典
        """
        try:
            # 首先加载默认配置
            default_config = {
                "default_settings": {
                    "interval": 100,
                    "min_interval": 80,
                    "max_interval": 120,
                    "count": -1,
                    "button": "left",
                    "click_type": "single",
                    "position_type": "current",
                    "fixed_position": {"x": 0, "y": 0},
                    "hotkeys": {
                        "start": "f6",
                        "stop": "f7",
                        "pause": "f8"
                    },
                    "randomize": True,
                    "sound_effects": False,
                    "dark_mode": False,
                    "multi_position": False,
                    "positions": [
                        {
                            "x": 0,
                            "y": 0,
                            "note": "默认位置",
                            "enabled": True,
                            "text": "",
                            "text_interval": 1000
                        }
                    ]
                },
                "app_settings": {
                    "language": "zh",
                    "check_for_updates": True,
                    "logging_enabled": False,
                    "log_level": "INFO"
                }
            }

            # 如果配置文件存在，则加载并合并配置
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                # 合并default_settings
                if "default_settings" in user_config:
                    default_config["default_settings"].update(user_config["default_settings"])
                
                # 合并app_settings
                if "app_settings" in user_config:
                    default_config["app_settings"].update(user_config["app_settings"])
                
            return default_config
        except Exception as e:
            print(f"加载配置出错: {e}")
            # 如果加载失败，创建并返回默认配置
            self._create_default_config()
            return self.load_config()

    def save_config(self, config):
        """保存配置文件
        Args:
            config: 配置字典
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置出错: {e}")
            return False