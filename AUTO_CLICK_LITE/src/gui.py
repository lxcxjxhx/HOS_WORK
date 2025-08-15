#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI模块 - 提供图形用户界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import pyautogui

class GUI:
    def __init__(self, settings, on_start=None, on_stop=None, on_pause=None, on_settings_change=None):
        """初始化GUI
        Args:
            settings: 设置字典
            on_start: 启动回调函数
            on_stop: 停止回调函数
            on_pause: 暂停/恢复回调函数
            on_settings_change: 设置更改回调函数
        """
        self.settings = settings
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_pause = on_pause
        self.on_settings_change = on_settings_change
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("连点器")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 设置中文字体
        self.font = ("SimHei", 10)
        
        # 创建样式
        self.style = ttk.Style()
        if self.settings['default_settings']['dark_mode']:
            self._set_dark_theme()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始化位置列表
        self.positions = self.settings['default_settings']['positions']
        # 初始化树视图禁用状态
        self.positions_tree_disabled = not self.settings['default_settings']['multi_position']
        
        # 创建UI元素
        self._create_widgets()
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=self.font)
        self.status_label.pack(side=tk.BOTTOM, pady=10)

    def _set_dark_theme(self):
        """设置暗黑主题"""
        self.style.configure("TLabel", background="#333333", foreground="#FFFFFF")
        self.style.configure("TButton", background="#555555", foreground="#FFFFFF")
        self.style.configure("TCheckbutton", background="#333333", foreground="#FFFFFF")
        self.style.configure("TCombobox", background="#555555", foreground="#FFFFFF")
        self.style.configure("TEntry", background="#555555", foreground="#FFFFFF")
        self.main_frame.configure(background="#333333")
        self.root.configure(background="#333333")

    def _create_widgets(self):
        """创建UI控件"""
        # 点击设置框架
        click_settings_frame = ttk.LabelFrame(self.main_frame, text="点击设置", padding="10")
        click_settings_frame.pack(fill=tk.X, pady=5)
        
        # 间隔设置
        ttk.Label(click_settings_frame, text="点击间隔(毫秒):", font=self.font).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.IntVar(value=self.settings['default_settings']['interval'])
        self.interval_entry = ttk.Entry(click_settings_frame, textvariable=self.interval_var, width=10)
        self.interval_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 随机间隔
        self.randomize_var = tk.BooleanVar(value=self.settings['default_settings']['randomize'])
        randomize_check = ttk.Checkbutton(click_settings_frame, text="启用随机间隔", variable=self.randomize_var,
                                         command=self._toggle_random_interval)
        randomize_check.grid(row=0, column=2, padx=5, pady=5)
        
        # 最小间隔
        ttk.Label(click_settings_frame, text="最小间隔(毫秒):", font=self.font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.min_interval_var = tk.IntVar(value=self.settings['default_settings']['min_interval'])
        self.min_interval_entry = ttk.Entry(click_settings_frame, textvariable=self.min_interval_var, width=10)
        self.min_interval_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 最大间隔
        ttk.Label(click_settings_frame, text="最大间隔(毫秒):", font=self.font).grid(row=1, column=2, sticky=tk.W, pady=5)
        self.max_interval_var = tk.IntVar(value=self.settings['default_settings']['max_interval'])
        self.max_interval_entry = ttk.Entry(click_settings_frame, textvariable=self.max_interval_var, width=10)
        self.max_interval_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # 点击次数
        ttk.Label(click_settings_frame, text="点击次数(-1=无限):", font=self.font).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.count_var = tk.IntVar(value=self.settings['default_settings']['count'])
        self.count_entry = ttk.Entry(click_settings_frame, textvariable=self.count_var, width=10)
        self.count_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 点击按钮
        ttk.Label(click_settings_frame, text="点击按钮:", font=self.font).grid(row=2, column=2, sticky=tk.W, pady=5)
        self.button_var = tk.StringVar(value=self.settings['default_settings']['button'])
        self.button_combobox = ttk.Combobox(click_settings_frame, textvariable=self.button_var, values=['left', 'right', 'middle'], width=8)
        self.button_combobox.grid(row=2, column=3, padx=5, pady=5)
        
        # 多位置模式
        self.multi_position_var = tk.BooleanVar(value=self.settings['default_settings']['multi_position'])
        multi_position_check = ttk.Checkbutton(click_settings_frame, text="启用多位置模式", variable=self.multi_position_var,
                                               command=self._toggle_multi_position)
        multi_position_check.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # 位置列表框架
        self.positions_frame = ttk.LabelFrame(self.main_frame, text="位置列表", padding="10")
        self.positions_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 位置列表
        columns = ('index', 'note', 'x', 'y', 'enabled', 'text', 'text_interval')
        self.positions_tree = ttk.Treeview(self.positions_frame, columns=columns, show='headings', height=8)
        # 绑定事件
        self.positions_tree.bind('<Button-1>', self._on_tree_click)
        self.positions_tree.bind('<Double-1>', self._on_tree_double_click)
        
        # 设置列标题
        self.positions_tree.heading('index', text='序号')
        self.positions_tree.heading('note', text='备注')
        self.positions_tree.heading('x', text='X坐标')
        self.positions_tree.heading('y', text='Y坐标')
        self.positions_tree.heading('enabled', text='启用')
        self.positions_tree.heading('text', text='文本内容')
        self.positions_tree.heading('text_interval', text='文本间隔(ms)')
        
        # 设置列宽
        self.positions_tree.column('index', width=50, anchor=tk.CENTER)
        self.positions_tree.column('note', width=100, anchor=tk.W)
        self.positions_tree.column('x', width=70, anchor=tk.CENTER)
        self.positions_tree.column('y', width=70, anchor=tk.CENTER)
        self.positions_tree.column('enabled', width=50, anchor=tk.CENTER)
        self.positions_tree.column('text', width=150, anchor=tk.W)
        self.positions_tree.column('text_interval', width=80, anchor=tk.CENTER)
        
        self.positions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.positions_frame, orient=tk.VERTICAL, command=self.positions_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.positions_tree.configure(yscroll=scrollbar.set)
        
        # 位置操作按钮框架
        self.pos_buttons_frame = ttk.Frame(self.main_frame, padding="10")
        self.pos_buttons_frame.pack(fill=tk.X, pady=5)
        
        # 添加位置按钮
        add_pos_button = ttk.Button(self.pos_buttons_frame, text="添加位置", command=self._add_position, width=10)
        add_pos_button.pack(side=tk.LEFT, padx=5)
        
        # 编辑位置按钮
        edit_pos_button = ttk.Button(self.pos_buttons_frame, text="编辑位置", command=self._edit_position, width=10)
        edit_pos_button.pack(side=tk.LEFT, padx=5)
        
        # 删除位置按钮
        delete_pos_button = ttk.Button(self.pos_buttons_frame, text="删除位置", command=self._delete_position, width=10)
        delete_pos_button.pack(side=tk.LEFT, padx=5)
        
        # 获取当前位置按钮
        get_current_pos_button = ttk.Button(self.pos_buttons_frame, text="获取当前位置", command=self._get_current_position_for_list, width=12)
        get_current_pos_button.pack(side=tk.LEFT, padx=5)
        
        # 控制按钮框架
        control_frame = ttk.Frame(self.main_frame, padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        
        # 启动按钮
        start_button = ttk.Button(control_frame, text="启动(F6)", command=self._on_start_click, width=10)
        start_button.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        stop_button = ttk.Button(control_frame, text="停止(F7)", command=self._on_stop_click, width=10)
        stop_button.pack(side=tk.LEFT, padx=5)
        
        # 暂停/恢复按钮
        pause_button = ttk.Button(control_frame, text="暂停/恢复(F8)", command=self._on_pause_click, width=12)
        pause_button.pack(side=tk.LEFT, padx=5)
        
        # 应用设置按钮
        apply_button = ttk.Button(control_frame, text="应用设置", command=self._apply_settings, width=10)
        apply_button.pack(side=tk.RIGHT, padx=5)
        
        # 加载位置列表
        self._load_positions()
        
        # 根据当前设置启用/禁用多位置相关控件
        self._toggle_multi_position()

    def _toggle_random_interval(self):
        """切换随机间隔启用状态"""
        state = 'normal' if self.randomize_var.get() else 'disabled'
        # 禁用/启用最小和最大间隔输入框
        self.min_interval_entry.config(state=state)
        self.max_interval_entry.config(state=state)

    def _toggle_multi_position(self):
        """切换多位置模式"""
        state = 'normal' if self.multi_position_var.get() else 'disabled'
        # 设置禁用标志
        self.positions_tree_disabled = (state == 'disabled')
        # 禁用/启用多位置相关控件
        # Treeview控件不支持state选项，通过控制相关按钮和绑定事件来实现禁用效果
        # 创建禁用样式
        if state == 'disabled':
            # 尝试创建一个禁用样式
            try:
                self.style.configure('Disabled.Treeview', background='#f0f0f0', foreground='#a0a0a0')
                self.positions_tree.configure(style='Disabled.Treeview')
            except Exception as e:
                # 如果创建样式失败，只使用事件绑定来阻止交互
                pass
        else:
            # 恢复默认样式
            try:
                self.positions_tree.configure(style='TTreeview')
            except Exception as e:
                pass
        for child in self.positions_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=state)
        for child in self.pos_buttons_frame.winfo_children():
            child.config(state=state)

    def _on_tree_click(self, event):
        """处理树视图点击事件"""
        if self.positions_tree_disabled:
            return 'break'  # 阻止事件传播

    def _on_tree_double_click(self, event):
        """处理树视图双击事件 - 双击获取鼠标位置"""
        if self.positions_tree_disabled:
            return 'break'  # 阻止事件传播
        self._get_position_on_double_click()

    def _get_position_on_double_click(self):
        """双击获取鼠标位置并添加到列表"""
        # 延迟获取位置，以便用户有时间移动鼠标
        def get_pos_delay():
            time.sleep(1)
            x, y = pyautogui.position()
            
            # 创建新位置
            new_pos = {
                'x': x,
                'y': y,
                'note': f'位置{len(self.positions)+1}',
                'enabled': True,
                'text': '',
                'text_interval': 1000
            }
            
            self.positions.append(new_pos)
            self.root.after(0, self._load_positions)
            
        threading.Thread(target=get_pos_delay, daemon=True).start()
        self.status_var.set("请移动鼠标到目标位置...")

    def _load_positions(self):
        """加载位置列表"""
        # 清空现有项
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        # 添加位置项
        for i, pos in enumerate(self.positions):
            self.positions_tree.insert('', tk.END, values=(i+1, pos['note'], pos['x'], pos['y'],
                                                          '是' if pos['enabled'] else '否',
                                                          pos['text'], pos['text_interval']))

    def _add_position(self):
        """添加新位置"""
        # 创建默认位置
        new_pos = {
            'x': 0,
            'y': 0,
            'note': f'位置{len(self.positions)+1}',
            'enabled': True,
            'text': '',
            'text_interval': 1000
        }
        
        # 打开编辑对话框
        if self._show_position_dialog(new_pos):
            self.positions.append(new_pos)
            self._load_positions()

    def _edit_position(self):
        """编辑选中的位置"""
        selected_items = self.positions_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择一个位置")
            return
        
        item = selected_items[0]
        index = int(self.positions_tree.item(item, 'values')[0]) - 1
        pos = self.positions[index]
        
        # 打开编辑对话框
        if self._show_position_dialog(pos):
            self.positions[index] = pos
            self._load_positions()

    def _delete_position(self):
        """删除选中的位置"""
        selected_items = self.positions_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择一个位置")
            return
        
        item = selected_items[0]
        index = int(self.positions_tree.item(item, 'values')[0]) - 1
        
        if messagebox.askyesno("确认", f"确定要删除'{self.positions[index]['note']}'吗?"):
            del self.positions[index]
            self._load_positions()

    def _get_current_position_for_list(self):
        """获取当前鼠标位置并添加到列表"""
        # 延迟获取位置，以便用户有时间移动鼠标
        def get_pos_delay():
            time.sleep(2)
            x, y = pyautogui.position()
            
            # 创建新位置
            new_pos = {
                'x': x,
                'y': y,
                'note': f'位置{len(self.positions)+1}',
                'enabled': True,
                'text': '',
                'text_interval': 1000
            }
            
            self.positions.append(new_pos)
            self.root.after(0, self._load_positions)
            messagebox.showinfo("提示", f"已添加当前位置: X={x}, Y={y}")

        threading.Thread(target=get_pos_delay, daemon=True).start()
        messagebox.showinfo("提示", "请在2秒内移动鼠标到目标位置...")

    def _show_position_dialog(self, pos):
        """显示位置编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑位置")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 备注
        ttk.Label(dialog, text="备注:", font=self.font).grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        note_var = tk.StringVar(value=pos['note'])
        ttk.Entry(dialog, textvariable=note_var, width=30).grid(row=0, column=1, pady=5)
        
        # X坐标
        ttk.Label(dialog, text="X坐标:", font=self.font).grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        x_var = tk.IntVar(value=pos['x'])
        ttk.Entry(dialog, textvariable=x_var, width=10).grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Y坐标
        ttk.Label(dialog, text="Y坐标:", font=self.font).grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        y_var = tk.IntVar(value=pos['y'])
        ttk.Entry(dialog, textvariable=y_var, width=10).grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # 启用状态
        enabled_var = tk.BooleanVar(value=pos['enabled'])
        ttk.Checkbutton(dialog, text="启用", variable=enabled_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5, padx=10)
        
        # 文本内容
        ttk.Label(dialog, text="文本内容:", font=self.font).grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        text_var = tk.StringVar(value=pos['text'])
        ttk.Entry(dialog, textvariable=text_var, width=30).grid(row=4, column=1, pady=5)
        
        # 文本间隔
        ttk.Label(dialog, text="文本间隔(毫秒):", font=self.font).grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        text_interval_var = tk.IntVar(value=pos['text_interval'])
        ttk.Entry(dialog, textvariable=text_interval_var, width=10).grid(row=5, column=1, pady=5, sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        # 确定按钮
        def on_ok():
            pos['note'] = note_var.get()
            pos['x'] = x_var.get()
            pos['y'] = y_var.get()
            pos['enabled'] = enabled_var.get()
            pos['text'] = text_var.get()
            pos['text_interval'] = text_interval_var.get()
            dialog.destroy()
            return True
        
        ttk.Button(button_frame, text="确定", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=10)
        
        self.root.wait_window(dialog)
        return True

    def _get_current_position(self):
        """获取当前鼠标位置"""
        # 延迟获取位置，以便用户有时间移动鼠标
        def get_pos_delay():
            time.sleep(2)
            x, y = pyautogui.position()
            self.fixed_x_var.set(x)
            self.fixed_y_var.set(y)
            messagebox.showinfo("提示", f"已获取当前位置: X={x}, Y={y}")

        threading.Thread(target=get_pos_delay, daemon=True).start()
        messagebox.showinfo("提示", "请在2秒内移动鼠标到目标位置...")

    def _on_start_click(self):
        """启动按钮点击事件"""
        if self.on_start:
            self.on_start()

    def _on_stop_click(self):
        """停止按钮点击事件"""
        if self.on_stop:
            self.on_stop()

    def _on_pause_click(self):
        """暂停/恢复按钮点击事件"""
        if self.on_pause:
            self.on_pause()

    def _apply_settings(self):
        """应用设置"""
        try:
            # 更新设置
            self.settings['default_settings']['interval'] = self.interval_var.get()
            self.settings['default_settings']['randomize'] = self.randomize_var.get()
            self.settings['default_settings']['min_interval'] = self.min_interval_var.get()
            self.settings['default_settings']['max_interval'] = self.max_interval_var.get()
            self.settings['default_settings']['count'] = self.count_var.get()
            self.settings['default_settings']['button'] = self.button_var.get()
            self.settings['default_settings']['multi_position'] = self.multi_position_var.get()
            self.settings['default_settings']['positions'] = self.positions
            
            # 调用回调函数
            if self.on_settings_change:
                self.on_settings_change(self.settings)
                
            messagebox.showinfo("成功", "设置已应用")
        except Exception as e:
            messagebox.showerror("错误", f"应用设置失败: {e}")

    def update_status(self, status):
        """更新状态标签"""
        self.status_var.set(status)

    def run(self):
        """运行GUI主循环"""
        self.root.mainloop()