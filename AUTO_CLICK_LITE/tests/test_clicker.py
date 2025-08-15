#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""点击模块测试"""
import unittest
import time
from src.clicker import Clicker

class TestClicker(unittest.TestCase):
    def setUp(self):
        """测试前设置"""
        self.clicker = Clicker(interval=100, count=5, button='left', randomize=False)

    def test_update_settings(self):
        """测试更新设置"""
        self.clicker.update_settings(interval=200, count=10, button='right')
        self.assertEqual(self.clicker.interval, 0.2)  # 转换为秒
        self.assertEqual(self.clicker.count, 10)
        self.assertEqual(self.clicker.button, 'right')

    def test_start_stop_clicking(self):
        """测试启动和停止点击"""
        # 启动点击
        self.clicker.start_clicking()
        # 等待一小段时间
        time.sleep(0.2)
        # 停止点击
        self.clicker.stop_clicking()
        # 确保点击已停止
        self.assertTrue(self.clicker._stop_event.is_set())

    def test_pause_resume_clicking(self):
        """测试暂停和恢复点击"""
        # 启动点击
        self.clicker.start_clicking()
        # 等待一小段时间
        time.sleep(0.2)
        # 暂停点击
        self.clicker.pause_clicking()
        self.assertTrue(self.clicker._pause_event.is_set())
        # 等待一小段时间
        time.sleep(0.2)
        # 恢复点击
        self.clicker.resume_clicking()
        self.assertFalse(self.clicker._pause_event.is_set())
        # 停止点击
        self.clicker.stop_clicking()

    def test_multi_position_mode(self):
        """测试多位置模式"""
        # 初始化多位置模式
        positions = [
            {'x': 100, 'y': 200, 'note': '位置1', 'enabled': True, 'text': '文本1', 'text_interval': 500},
            {'x': 300, 'y': 400, 'note': '位置2', 'enabled': True, 'text': '文本2', 'text_interval': 1000},
        ]
        self.clicker = Clicker(interval=100, count=5, button='left', randomize=False,
                              multi_position=True, positions=positions)
        
        # 验证初始化
        self.assertTrue(self.clicker.multi_position)
        self.assertEqual(len(self.clicker.positions), 2)
        self.assertEqual(self.clicker.positions[0]['x'], 100)
        self.assertEqual(self.clicker.positions[1]['text'], '文本2')
        
        # 更新多位置设置
        new_positions = [
            {'x': 150, 'y': 250, 'note': '新位置1', 'enabled': True, 'text': '新文本1', 'text_interval': 600},
        ]
        self.clicker.update_settings(multi_position=True, positions=new_positions)
        self.assertEqual(len(self.clicker.positions), 1)
        self.assertEqual(self.clicker.positions[0]['note'], '新位置1')
        self.assertEqual(self.clicker.positions[0]['text_interval'], 600)

    def test_disabled_positions(self):
        """测试禁用位置"""
        positions = [
            {'x': 100, 'y': 200, 'note': '位置1', 'enabled': True, 'text': '文本1', 'text_interval': 500},
            {'x': 300, 'y': 400, 'note': '位置2', 'enabled': False, 'text': '文本2', 'text_interval': 1000}
        ]
        self.clicker = Clicker(interval=100, count=5, button='left', randomize=False, multi_position=True, positions=positions)
        
        # 验证只有启用的位置被处理
        active_positions = [pos for pos in self.clicker.positions if pos['enabled']]
        self.assertEqual(len(active_positions), 1)
        self.assertEqual(active_positions[0]['note'], '位置1')

    def test_text_input(self):
        """测试文本输入功能"""
        positions = [
            {'x': 100, 'y': 200, 'note': '文本位置', 'enabled': True, 'text': '测试文本', 'text_interval': 500}
        ]
        self.clicker = Clicker(interval=100, count=5, button='left', randomize=False, multi_position=True, positions=positions)
        
        # 验证文本输入设置
        self.assertEqual(self.clicker.positions[0]['text'], '测试文本')
        self.assertEqual(self.clicker.positions[0]['text_interval'], 500)

if __name__ == '__main__':
    unittest.main()