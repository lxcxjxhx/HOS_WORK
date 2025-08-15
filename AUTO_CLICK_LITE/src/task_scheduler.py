#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度器 - 支持定时任务和批量任务管理
"""
import time
import json
import threading
from datetime import datetime, timedelta
import schedule
from concurrent.futures import ThreadPoolExecutor, as_completed

class TaskScheduler:
    def __init__(self, max_workers=5):
        """初始化任务调度器"""
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.scheduled_tasks = []
        self.running_tasks = {}
        self.task_results = {}
        self.running = False
        
    def add_scheduled_task(self, task_config):
        """添加定时任务"""
        task_id = f"task_{len(self.scheduled_tasks)}"
        task_config['id'] = task_id
        task_config['created_at'] = datetime.now().isoformat()
        self.scheduled_tasks.append(task_config)
        
        # 根据调度类型设置任务
        if task_config['schedule_type'] == 'interval':
            schedule.every(task_config['interval']).seconds.do(
                self._execute_task, task_config
            )
        elif task_config['schedule_type'] == 'daily':
            schedule.every().day.at(task_config['time']).do(
                self._execute_task, task_config
            )
        elif task_config['schedule_type'] == 'weekly':
            getattr(schedule.every(), task_config['day']).at(task_config['time']).do(
                self._execute_task, task_config
            )
        elif task_config['schedule_type'] == 'once':
            # 一次性任务，立即执行
            self._execute_task(task_config)
            
        return task_id
    
    def add_batch_task(self, tasks, parallel=True):
        """添加批量任务"""
        batch_id = f"batch_{int(time.time())}"
        
        if parallel:
            # 并行执行
            futures = []
            for task in tasks:
                future = self.executor.submit(self._execute_single_task, task)
                futures.append(future)
                self.running_tasks[f"{batch_id}_{len(futures)}"] = future
            
            # 等待所有任务完成
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({'status': 'error', 'error': str(e)})
            
            self.task_results[batch_id] = results
        else:
            # 串行执行
            results = []
            for i, task in enumerate(tasks):
                task_id = f"{batch_id}_{i}"
                try:
                    result = self._execute_single_task(task)
                    results.append(result)
                except Exception as e:
                    results.append({'status': 'error', 'error': str(e)})
            
            self.task_results[batch_id] = results
        
        return batch_id
    
    def _execute_task(self, task_config):
        """执行单个任务"""
        task_id = task_config['id']
        
        try:
            # 根据任务类型执行不同的操作
            if task_config['type'] == 'web_automation':
                from web_automation import WebAutomation
                web_auto = WebAutomation()
                result = web_auto.execute_batch_tasks(task_config['tasks'])
                web_auto.close_all_drivers()
                
            elif task_config['type'] == 'click_automation':
                from clicker import Clicker
                clicker = Clicker(**task_config['clicker_config'])
                clicker.start_clicking()
                result = {'status': 'completed', 'type': 'click_automation'}
                
            elif task_config['type'] == 'data_processing':
                result = self._process_data(task_config['data_config'])
                
            elif task_config['type'] == 'api_requests':
                result = self._make_api_requests(task_config['api_config'])
            
            else:
                result = {'status': 'error', 'error': f'Unknown task type: {task_config["type"]}'}
            
            # 保存结果
            self.task_results[task_id] = {
                'task_id': task_id,
                'status': 'completed',
                'result': result,
                'completed_at': datetime.now().isoformat()
            }
            
            # 如果配置了结果处理，执行后续操作
            if task_config.get('on_complete'):
                self._handle_task_completion(task_config, result)
                
        except Exception as e:
            self.task_results[task_id] = {
                'task_id': task_id,
                'status': 'error',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            }
    
    def _execute_single_task(self, task):
        """执行单个任务（用于批量任务）"""
        return self._execute_task(task)
    
    def _process_data(self, data_config):
        """数据处理任务"""
        results = []
        
        if data_config['action'] == 'csv_processing':
            import pandas as pd
            df = pd.read_csv(data_config['input_file'])
            
            # 执行数据处理操作
            for operation in data_config['operations']:
                if operation['type'] == 'filter':
                    df = df[df[operation['column']].str.contains(operation['value'])]
                elif operation['type'] == 'transform':
                    df[operation['column']] = df[operation['column']].apply(eval(operation['function']))
                elif operation['type'] == 'aggregate':
                    df = df.groupby(operation['group_by']).agg(operation['aggregations'])
            
            # 保存处理后的数据
            df.to_csv(data_config['output_file'], index=False)
            results.append({'status': 'success', 'rows_processed': len(df)})
            
        elif data_config['action'] == 'json_processing':
            with open(data_config['input_file'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理JSON数据
            processed_data = self._process_json_data(data, data_config['operations'])
            
            with open(data_config['output_file'], 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            results.append({'status': 'success', 'items_processed': len(processed_data)})
        
        return results
    
    def _make_api_requests(self, api_config):
        """API请求任务"""
        import requests
        results = []
        
        for request_config in api_config['requests']:
            try:
                response = requests.request(
                    method=request_config['method'],
                    url=request_config['url'],
                    headers=request_config.get('headers', {}),
                    data=request_config.get('data'),
                    json=request_config.get('json'),
                    params=request_config.get('params'),
                    timeout=request_config.get('timeout', 30)
                )
                
                results.append({
                    'url': request_config['url'],
                    'status_code': response.status_code,
                    'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    'status': 'success'
                })
                
            except Exception as e:
                results.append({
                    'url': request_config['url'],
                    'status': 'error',
                    'error': str(e)
                })
            
            # 请求间延迟
            if request_config.get('delay'):
                time.sleep(request_config['delay'])
        
        return results
    
    def _process_json_data(self, data, operations):
        """处理JSON数据"""
        for operation in operations:
            if operation['type'] == 'filter':
                if isinstance(data, list):
                    data = [item for item in data if self._evaluate_condition(item, operation['condition'])]
            elif operation['type'] == 'transform':
                if isinstance(data, list):
                    for item in data:
                        if operation['field'] in item:
                            item[operation['field']] = eval(operation['function'])(item[operation['field']])
            elif operation['type'] == 'extract':
                if isinstance(data, list):
                    data = [item.get(operation['field']) for item in data if operation['field'] in item]
        
        return data
    
    def _evaluate_condition(self, item, condition):
        """评估条件"""
        field = condition['field']
        operator = condition['operator']
        value = condition['value']
        
        if field not in item:
            return False
        
        item_value = item[field]
        
        if operator == 'equals':
            return item_value == value
        elif operator == 'contains':
            return value in str(item_value)
        elif operator == 'greater_than':
            return float(item_value) > float(value)
        elif operator == 'less_than':
            return float(item_value) < float(value)
        
        return False
    
    def _handle_task_completion(self, task_config, result):
        """处理任务完成后的操作"""
        completion_config = task_config['on_complete']
        
        if completion_config['action'] == 'send_email':
            self._send_email_notification(completion_config, result)
        elif completion_config['action'] == 'save_to_database':
            self._save_to_database(completion_config, result)
        elif completion_config['action'] == 'trigger_webhook':
            self._trigger_webhook(completion_config, result)
    
    def _send_email_notification(self, config, result):
        """发送邮件通知"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = config['from_email']
        msg['To'] = config['to_email']
        msg['Subject'] = config['subject']
        
        body = f"任务执行完成\n\n结果: {json.dumps(result, indent=2, ensure_ascii=False)}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['username'], config['password'])
        server.send_message(msg)
        server.quit()
    
    def _save_to_database(self, config, result):
        """保存到数据库"""
        # 这里可以集成各种数据库
        pass
    
    def _trigger_webhook(self, config, result):
        """触发Webhook"""
        import requests
        
        payload = {
            'task_completed': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        requests.post(config['webhook_url'], json=payload)
    
    def start_scheduler(self):
        """启动调度器"""
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        self.executor.shutdown(wait=True)
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        if task_id in self.task_results:
            return self.task_results[task_id]
        elif task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            if future.done():
                return {'status': 'completed', 'result': future.result()}
            else:
                return {'status': 'running'}
        else:
            return {'status': 'not_found'}
    
    def get_all_tasks(self):
        """获取所有任务"""
        return {
            'scheduled_tasks': self.scheduled_tasks,
            'task_results': self.task_results,
            'running_tasks': list(self.running_tasks.keys())
        }
    
    def cancel_task(self, task_id):
        """取消任务"""
        if task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            future.cancel()
            del self.running_tasks[task_id]
            return True
        return False