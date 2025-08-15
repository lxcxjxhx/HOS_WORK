#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页自动化模块 - 支持批量网页操作
"""
import time
import json
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import pyautogui

class WebAutomation:
    def __init__(self):
        """初始化网页自动化"""
        self.drivers = []  # 多浏览器实例
        self.tasks = []    # 任务队列
        self.running = False
        self.paused = False
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
    def create_driver(self, headless=False, user_agent=None, proxy=None):
        """创建浏览器驱动"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if user_agent:
            options.add_argument(f'--user-agent={user_agent}')
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.drivers.append(driver)
        return driver
    
    def batch_open_urls(self, urls, max_tabs=10):
        """批量打开网页"""
        driver = self.create_driver()
        
        for i, url in enumerate(urls[:max_tabs]):
            if i == 0:
                driver.get(url)
            else:
                driver.execute_script(f"window.open('{url}', '_blank');")
            time.sleep(random.uniform(1, 3))  # 随机延迟
            
        return driver
    
    def batch_fill_forms(self, driver, form_data_list):
        """批量填写表单"""
        results = []
        
        for tab_index, form_data in enumerate(form_data_list):
            try:
                # 切换到指定标签页
                driver.switch_to.window(driver.window_handles[tab_index])
                
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 填写表单字段
                for field in form_data.get('fields', []):
                    element = self._find_element(driver, field['selector'], field['by'])
                    if element:
                        if field['action'] == 'input':
                            element.clear()
                            element.send_keys(field['value'])
                        elif field['action'] == 'click':
                            element.click()
                        elif field['action'] == 'select':
                            from selenium.webdriver.support.ui import Select
                            select = Select(element)
                            select.select_by_visible_text(field['value'])
                            
                        time.sleep(random.uniform(0.5, 1.5))
                
                # 提交表单（如果需要）
                if form_data.get('submit'):
                    submit_btn = self._find_element(driver, form_data['submit']['selector'], form_data['submit']['by'])
                    if submit_btn:
                        submit_btn.click()
                        time.sleep(random.uniform(2, 4))
                
                results.append({'tab': tab_index, 'status': 'success'})
                
            except Exception as e:
                results.append({'tab': tab_index, 'status': 'error', 'error': str(e)})
                
        return results
    
    def batch_scrape_data(self, driver, scrape_configs):
        """批量抓取数据"""
        results = []
        
        for tab_index, config in enumerate(scrape_configs):
            try:
                driver.switch_to.window(driver.window_handles[tab_index])
                
                data = {}
                for field in config.get('fields', []):
                    elements = driver.find_elements(getattr(By, field['by'].upper()), field['selector'])
                    
                    if field.get('multiple', False):
                        data[field['name']] = [elem.text or elem.get_attribute('value') for elem in elements]
                    else:
                        data[field['name']] = elements[0].text or elements[0].get_attribute('value') if elements else None
                
                results.append({'tab': tab_index, 'data': data, 'status': 'success'})
                
            except Exception as e:
                results.append({'tab': tab_index, 'status': 'error', 'error': str(e)})
                
        return results
    
    def batch_social_actions(self, driver, actions_config):
        """批量社交媒体操作（点赞、关注、评论等）"""
        results = []
        
        for tab_index, config in enumerate(actions_config):
            try:
                driver.switch_to.window(driver.window_handles[tab_index])
                
                for action in config.get('actions', []):
                    if action['type'] == 'like':
                        like_btn = self._find_element(driver, action['selector'], action['by'])
                        if like_btn and not like_btn.get_attribute('class').__contains__('liked'):
                            like_btn.click()
                            
                    elif action['type'] == 'follow':
                        follow_btn = self._find_element(driver, action['selector'], action['by'])
                        if follow_btn and follow_btn.text.lower() in ['follow', '关注']:
                            follow_btn.click()
                            
                    elif action['type'] == 'comment':
                        comment_box = self._find_element(driver, action['selector'], action['by'])
                        if comment_box:
                            comment_box.click()
                            comment_box.send_keys(action['text'])
                            # 查找并点击发送按钮
                            send_btn = self._find_element(driver, action.get('send_selector', '[type="submit"]'), action.get('send_by', 'css'))
                            if send_btn:
                                send_btn.click()
                    
                    time.sleep(random.uniform(2, 5))  # 随机延迟避免检测
                
                results.append({'tab': tab_index, 'status': 'success'})
                
            except Exception as e:
                results.append({'tab': tab_index, 'status': 'error', 'error': str(e)})
                
        return results
    
    def batch_shopping_actions(self, driver, shopping_configs):
        """批量购物操作（加购物车、下单等）"""
        results = []
        
        for tab_index, config in enumerate(shopping_configs):
            try:
                driver.switch_to.window(driver.window_handles[tab_index])
                
                # 选择商品规格
                if config.get('specifications'):
                    for spec in config['specifications']:
                        spec_element = self._find_element(driver, spec['selector'], spec['by'])
                        if spec_element:
                            spec_element.click()
                            time.sleep(1)
                
                # 设置数量
                if config.get('quantity'):
                    qty_input = self._find_element(driver, config['quantity']['selector'], config['quantity']['by'])
                    if qty_input:
                        qty_input.clear()
                        qty_input.send_keys(str(config['quantity']['value']))
                
                # 加入购物车或立即购买
                if config.get('action') == 'add_to_cart':
                    cart_btn = self._find_element(driver, config['cart_selector'], config['cart_by'])
                    if cart_btn:
                        cart_btn.click()
                elif config.get('action') == 'buy_now':
                    buy_btn = self._find_element(driver, config['buy_selector'], config['buy_by'])
                    if buy_btn:
                        buy_btn.click()
                
                time.sleep(random.uniform(2, 4))
                results.append({'tab': tab_index, 'status': 'success'})
                
            except Exception as e:
                results.append({'tab': tab_index, 'status': 'error', 'error': str(e)})
                
        return results
    
    def batch_account_operations(self, driver, account_configs):
        """批量账号操作（注册、登录等）"""
        results = []
        
        for tab_index, config in enumerate(account_configs):
            try:
                driver.switch_to.window(driver.window_handles[tab_index])
                
                if config['action'] == 'register':
                    # 填写注册表单
                    for field, value in config['data'].items():
                        element = self._find_element(driver, f'[name="{field}"]', 'css')
                        if element:
                            element.clear()
                            element.send_keys(value)
                            time.sleep(random.uniform(0.5, 1))
                    
                    # 处理验证码（如果需要）
                    if config.get('captcha'):
                        self._handle_captcha(driver, config['captcha'])
                    
                    # 提交注册
                    submit_btn = self._find_element(driver, config['submit_selector'], config['submit_by'])
                    if submit_btn:
                        submit_btn.click()
                
                elif config['action'] == 'login':
                    # 登录操作
                    username_field = self._find_element(driver, config['username_selector'], config['username_by'])
                    password_field = self._find_element(driver, config['password_selector'], config['password_by'])
                    
                    if username_field and password_field:
                        username_field.clear()
                        username_field.send_keys(config['username'])
                        time.sleep(random.uniform(0.5, 1))
                        
                        password_field.clear()
                        password_field.send_keys(config['password'])
                        time.sleep(random.uniform(0.5, 1))
                        
                        login_btn = self._find_element(driver, config['login_selector'], config['login_by'])
                        if login_btn:
                            login_btn.click()
                
                time.sleep(random.uniform(3, 6))
                results.append({'tab': tab_index, 'status': 'success'})
                
            except Exception as e:
                results.append({'tab': tab_index, 'status': 'error', 'error': str(e)})
                
        return results
    
    def _find_element(self, driver, selector, by='css'):
        """查找元素"""
        try:
            by_mapping = {
                'css': By.CSS_SELECTOR,
                'xpath': By.XPATH,
                'id': By.ID,
                'class': By.CLASS_NAME,
                'name': By.NAME,
                'tag': By.TAG_NAME
            }
            
            return WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by_mapping.get(by, By.CSS_SELECTOR), selector))
            )
        except TimeoutException:
            return None
    
    def _handle_captcha(self, driver, captcha_config):
        """处理验证码"""
        if captcha_config['type'] == 'image':
            # 图片验证码处理
            captcha_img = self._find_element(driver, captcha_config['img_selector'], captcha_config['img_by'])
            if captcha_img:
                # 这里可以集成OCR服务或人工处理
                captcha_text = input("请输入验证码: ")  # 简单的人工输入
                captcha_input = self._find_element(driver, captcha_config['input_selector'], captcha_config['input_by'])
                if captcha_input:
                    captcha_input.send_keys(captcha_text)
    
    def execute_batch_tasks(self, tasks):
        """执行批量任务"""
        self.tasks = tasks
        self.running = True
        self._stop_event.clear()
        self._pause_event.clear()
        
        results = []
        
        for task in tasks:
            if self._stop_event.is_set():
                break
                
            # 检查暂停状态
            while self._pause_event.is_set() and not self._stop_event.is_set():
                time.sleep(0.1)
            
            try:
                if task['type'] == 'open_urls':
                    driver = self.batch_open_urls(task['urls'], task.get('max_tabs', 10))
                    results.append({'task': task['name'], 'status': 'success', 'driver_id': len(self.drivers)-1})
                    
                elif task['type'] == 'fill_forms':
                    driver = self.drivers[task['driver_id']]
                    result = self.batch_fill_forms(driver, task['form_data'])
                    results.append({'task': task['name'], 'status': 'success', 'results': result})
                    
                elif task['type'] == 'scrape_data':
                    driver = self.drivers[task['driver_id']]
                    result = self.batch_scrape_data(driver, task['scrape_configs'])
                    results.append({'task': task['name'], 'status': 'success', 'data': result})
                    
                elif task['type'] == 'social_actions':
                    driver = self.drivers[task['driver_id']]
                    result = self.batch_social_actions(driver, task['actions_config'])
                    results.append({'task': task['name'], 'status': 'success', 'results': result})
                    
                elif task['type'] == 'shopping_actions':
                    driver = self.drivers[task['driver_id']]
                    result = self.batch_shopping_actions(driver, task['shopping_configs'])
                    results.append({'task': task['name'], 'status': 'success', 'results': result})
                    
                elif task['type'] == 'account_operations':
                    driver = self.drivers[task['driver_id']]
                    result = self.batch_account_operations(driver, task['account_configs'])
                    results.append({'task': task['name'], 'status': 'success', 'results': result})
                
                # 任务间随机延迟
                time.sleep(random.uniform(task.get('delay_min', 1), task.get('delay_max', 3)))
                
            except Exception as e:
                results.append({'task': task['name'], 'status': 'error', 'error': str(e)})
        
        self.running = False
        return results
    
    def stop_tasks(self):
        """停止任务"""
        self._stop_event.set()
        self.running = False
    
    def pause_tasks(self):
        """暂停任务"""
        self._pause_event.set()
    
    def resume_tasks(self):
        """恢复任务"""
        self._pause_event.clear()
    
    def close_all_drivers(self):
        """关闭所有浏览器"""
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
    
    def save_results_to_file(self, results, filename):
        """保存结果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)