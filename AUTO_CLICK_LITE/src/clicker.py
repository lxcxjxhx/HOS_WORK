#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连点器核心模块 - 处理鼠标点击模拟
"""
import time
import random
import pyautogui
from threading import Event

class Clicker:
    def __init__(self, interval=100, count=-1, button='left', randomize=True,
                 min_interval=80, max_interval=120, position_type='current',
                 fixed_position={'x': 0, 'y': 0}, multi_position=False,
                 positions=None):
        """初始化点击器
        Args:
            interval: 点击间隔(毫秒)
            count: 点击次数(-1表示无限循环)
            button: 点击按钮(left, right, middle)
            randomize: 是否启用随机间隔
            min_interval: 最小随机间隔
            max_interval: 最大随机间隔
            position_type: 点击位置类型(current, fixed)
            fixed_position: 固定点击位置
            multi_position: 是否启用多位置模式
            positions: 多位置列表
        """
        self.interval = interval / 1000.0  # 转换为秒
        self.count = count
        self.button = button
        self.randomize = randomize
        self.min_interval = min_interval / 1000.0
        self.max_interval = max_interval / 1000.0
        self.position_type = position_type
        self.fixed_position = fixed_position
        self.multi_position = multi_position
        self.positions = positions if positions else [
            {
                "x": 0,
                "y": 0,
                "note": "默认位置",
                "enabled": True,
                "text": "",
                "text_interval": 1000
            }
        ]
        
        # 控制标志
        self._stop_event = Event()
        self._pause_event = Event()

    def update_settings(self, interval=None, count=None, button=None, randomize=None,
                       min_interval=None, max_interval=None, position_type=None,
                       fixed_position=None, multi_position=None, positions=None):
        """更新设置"""
        if interval is not None:
            self.interval = interval / 1000.0
        if count is not None:
            self.count = count
        if button is not None:
            self.button = button
        if randomize is not None:
            self.randomize = randomize
        if min_interval is not None:
            self.min_interval = min_interval / 1000.0
        if max_interval is not None:
            self.max_interval = max_interval / 1000.0
        if position_type is not None:
            self.position_type = position_type
        if fixed_position is not None:
            self.fixed_position = fixed_position
        if multi_position is not None:
            self.multi_position = multi_position
        if positions is not None:
            self.positions = positions

    def start_clicking(self):
        """开始点击"""
        self._stop_event.clear()
        self._pause_event.clear()

        click_count = 0
        while not self._stop_event.is_set():
            # 检查是否暂停
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue

            # 确定点击位置和执行点击
            try:
                if self.multi_position:
                    # 多位置模式
                    for pos in self.positions:
                        if not pos['enabled']:
                            continue

                        # 移动到指定位置
                        x, y = pos['x'], pos['y']
                        pyautogui.moveTo(x, y)

                        # 执行点击
                        pyautogui.click(button=self.button)
                        click_count += 1

                        # 如果有文本需要输入
                        print("===== 文本输入逻辑开始 ====")
                        print(f"检测到文本输入需求: '{pos['text']}'")
                        if pos['text']:
                            try:
                                # 获取当前鼠标位置
                                current_pos = pyautogui.position()
                                print(f"当前鼠标位置: {current_pos}")
                                  
                                # 方法1: 尝试直接点击文本框位置确保焦点
                                pyautogui.click(button=self.button)
                                print("已点击文本框位置")
                                time.sleep(0.3)  # 给足够时间让文本框获得焦点
                                
                                # 方法2: 使用键盘快捷键激活文本框
                                # 假设当前已经在正确的窗口，按Tab键切换到文本框
                                pyautogui.press('tab')
                                time.sleep(0.2)
                                print("已按下Tab键切换焦点")
                                
                                # 方法3: 使用鼠标移动到文本框并点击
                                pyautogui.moveTo(current_pos)
                                pyautogui.click(button=self.button)
                                time.sleep(0.2)
                                print("已再次点击文本框位置")
                                
                                # 确认当前活动窗口
                                try:
                                    active_window = pyautogui.getActiveWindowTitle()
                                    print(f"活动窗口: {active_window}")
                                except Exception as e:
                                    print(f"无法获取活动窗口: {e}")
                                  
                                # 清除文本框现有内容
                                pyautogui.hotkey('ctrl', 'a')
                                time.sleep(0.1)
                                pyautogui.press('delete')
                                time.sleep(0.1)
                                print("已清除文本框内容")
                                
                                # 使用剪贴板粘贴文本 (推荐方法)
                                print(f"准备粘贴文本: '{pos['text']}'")
                                try:
                                    import pyperclip
                                    # 复制文本到剪贴板
                                    pyperclip.copy(pos['text'])
                                    print(f"已复制文本到剪贴板: '{pos['text']}'")
                                    # 粘贴文本
                                    pyautogui.hotkey('ctrl', 'v')
                                    print(f"已粘贴文本: '{pos['text']}'")
                                except Exception as e:
                                    print(f"粘贴失败: {e}")
                                    # 如果粘贴失败，使用更可靠的输入方法
                                    # 使用pyautogui的write函数
                                    pyautogui.write(pos['text'], interval=0.05)
                                    print(f"已使用write函数输入文本: {pos['text']}")
                                    # 如果write函数失败，使用最后的回退方案
                                    try:
                                        pass
                                    except Exception as e:
                                        pyautogui.typewrite(pos['text'], interval=0.05)
                                        print(f"已使用typewrite输入文本: {pos['text']}")
                                
                                # 文本输入后的间隔
                                time.sleep(pos['text_interval'] / 1000.0)
                                print("===== 文本输入逻辑结束 ====")
                                 
                                # 文本输入后的间隔
                                time.sleep(pos['text_interval'] / 1000.0)
                            except Exception as e:
                                print(f"文本输入出错: {e}")

                        # 检查是否达到点击次数
                        if self.count > 0 and click_count >= self.count:
                            self._stop_event.set()
                            break

                        # 等待下一次点击
                        if self.randomize:
                            wait_time = random.uniform(self.min_interval, self.max_interval)
                        else:
                            wait_time = self.interval

                        time.sleep(wait_time)
                else:
                    # 单位置模式
                    if self.position_type == 'fixed':
                        x, y = self.fixed_position['x'], self.fixed_position['y']
                        pyautogui.moveTo(x, y)
                    # 如果是current，则不需要移动，使用当前位置

                    # 执行点击
                    pyautogui.click(button=self.button)
                    click_count += 1

                    # 检查是否达到点击次数
                    if self.count > 0 and click_count >= self.count:
                        break

                    # 等待下一次点击
                    if self.randomize:
                        wait_time = random.uniform(self.min_interval, self.max_interval)
                    else:
                        wait_time = self.interval

                    time.sleep(wait_time)
            except Exception as e:
                print(f"点击出错: {e}")
                time.sleep(0.1)

    def stop_clicking(self):
        """停止点击"""
        self._stop_event.set()

    def pause_clicking(self):
        """暂停点击"""
        self._pause_event.set()

    def resume_clicking(self):
        """
        恢复点击
        """
        self._pause_event.clear()