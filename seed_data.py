#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
种子数据生成脚本
生成50条拖延风险评估数据并插入到SQLite数据库
"""

import sqlite3
import os
import random
from datetime import datetime

# 数据库路径
db_path = 'data/risk_records.db'

# 风险等级计算函数
def get_risk_level(answers):
    """
    根据任务厌恶、结果价值和自我控制计算风险等级
    
    Args:
        answers (dict): 包含任务厌恶、结果价值和自我控制的字典
    
    Returns:
        str: 风险等级（低、中、高）
    """
    w1, w2, w3 = 0.4, 0.3, 0.3
    score = (
        answers["任务厌恶"] * w1 +
        (100 - answers["结果价值"]) * w2 +
        (100 - answers["自我控制"]) * w3
    )
    if score < 30:
        return "低"
    elif score < 70:
        return "中"
    else:
        return "高"

# 检查并初始化数据库
def init_db():
    """
    检查数据库和表是否存在，字段是否齐全
    如缺少字段则自动添加
    """
    # 确保data目录存在
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='risk_records'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        # 创建新表，包含所有字段
        cursor.execute('''
        CREATE TABLE risk_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_aversion INTEGER,
            result_value INTEGER NOT NULL,
            self_control INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            actual_delay INTEGER
        )
        ''')
        print("创建了新表 risk_records")
    else:
        # 检查表结构，添加缺失的列
        cursor.execute("PRAGMA table_info(risk_records)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加缺失的列
        if 'task_aversion' not in columns:
            cursor.execute("ALTER TABLE risk_records ADD COLUMN task_aversion INTEGER")
            print("添加了 task_aversion 列")
        
        if 'actual_delay' not in columns:
            cursor.execute("ALTER TABLE risk_records ADD COLUMN actual_delay INTEGER")
            print("添加了 actual_delay 列")
    
    conn.commit()
    conn.close()

# 定义六个场景的参数区间
scenarios = {
    # L1 低风-易做：任务厌恶 0–30，结果价值 70–100，自我控制 70–100，actual_delay=0 为主
    'L1': {
        'task_aversion': (0, 30),     # 低任务厌恶
        'result_value': (70, 100),    # 高结果价值
        'self_control': (70, 100),    # 高自我控制
        'actual_delay': lambda: 0 if random.random() < 0.9 else 1  # 90%概率不拖延
    },
    # L2 低风-价值驱动：任务厌恶 30–50，结果价值 60–90，自我控制 50–70，actual_delay=0/1 随机
    'L2': {
        'task_aversion': (30, 50),    # 中等偏低任务厌恶
        'result_value': (60, 90),     # 高结果价值
        'self_control': (50, 70),     # 中等自我控制
        'actual_delay': lambda: random.choice([0, 1])  # 随机拖延
    },
    # M1 中风-均衡：任务厌恶 40–60，结果价值 40–60，自我控制 40–60，actual_delay=0/1 随机
    'M1': {
        'task_aversion': (40, 60),    # 中等任务厌恶
        'result_value': (40, 60),     # 中等结果价值
        'self_control': (40, 60),     # 中等自我控制
        'actual_delay': lambda: random.choice([0, 1])  # 随机拖延
    },
    # M2 中风-高厌恶但高价值：任务厌恶 70–90，结果价值 80–100，自我控制 40–70，actual_delay=0/1 随机
    'M2': {
        'task_aversion': (70, 90),    # 高任务厌恶
        'result_value': (80, 100),    # 高结果价值
        'self_control': (40, 70),     # 中等自我控制
        'actual_delay': lambda: random.choice([0, 1])  # 随机拖延
    },
    # H1 高风险-全差：任务厌恶 80–100，结果价值 0–30，自我控制 0–30，actual_delay=1 为主
    'H1': {
        'task_aversion': (80, 100),   # 高任务厌恶
        'result_value': (0, 30),      # 低结果价值
        'self_control': (0, 30),      # 低自我控制
        'actual_delay': lambda: 1 if random.random() < 0.9 else 0  # 90%概率拖延
    },
    # H2 高风险-自控崩塌：任务厌恶 50–70，结果价值 40–70，自我控制 0–30，actual_delay=1 为主
    'H2': {
        'task_aversion': (50, 70),    # 中等任务厌恶
        'result_value': (40, 70),     # 中等结果价值
        'self_control': (0, 30),      # 低自我控制
        'actual_delay': lambda: 1 if random.random() < 0.9 else 0  # 90%概率拖延
    }
}

# 生成种子数据
def generate_seed_data():
    """
    生成50条种子数据
    
    Returns:
        list: 包含50条数据的列表
    """
    data = []
    
    # 计算每个场景需要生成的数据量
    # 6个场景，共50条数据，分配为：8, 8, 8, 8, 9, 9
    scenario_counts = {'L1': 8, 'L2': 8, 'M1': 8, 'M2': 8, 'H1': 9, 'H2': 9}
    
    # 每个场景生成指定数量的数据
    for scenario_name, params in scenarios.items():
        count = scenario_counts[scenario_name]
        for _ in range(count):
            # 生成随机值
            task_aversion = random.randint(*params['task_aversion'])
            result_value = random.randint(*params['result_value'])
            self_control = random.randint(*params['self_control'])
            
            # 确定是否拖延
            if 'actual_delay' in params:
                # 调用函数获取actual_delay值
                actual_delay = params['actual_delay']()
            else:
                # 根据风险等级决定是否拖延
                risk_level = get_risk_level({
                    "任务厌恶": task_aversion,
                    "结果价值": result_value,
                    "自我控制": self_control
                })
                if risk_level == "高":
                    actual_delay = 1
                elif risk_level == "中":
                    actual_delay = random.choice([0, 1])
                else:
                    actual_delay = 0
            
            # 生成时间戳和来源
            timestamp = datetime.now().isoformat()
            source = f"场景{scenario_name}"
            
            # 添加到数据列表
            data.append({
                'task_aversion': task_aversion,
                'result_value': result_value,
                'self_control': self_control,
                'actual_delay': actual_delay,
                'timestamp': timestamp,
                'source': source
            })
    
    return data

# 插入数据到数据库
def insert_data(data):
    """
    将数据插入到数据库
    
    Args:
        data (list): 要插入的数据列表
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 清空表中的现有数据
    cursor.execute("DELETE FROM risk_records")
    print("清空了现有数据")
    
    # 插入新数据
    for item in data:
        cursor.execute('''
        INSERT INTO risk_records (task_aversion, result_value, self_control, actual_delay, timestamp, source)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            item['task_aversion'],
            item['result_value'],
            item['self_control'],
            item['actual_delay'],
            item['timestamp'],
            item['source']
        ))
    
    conn.commit()
    conn.close()
    print(f"成功插入 {len(data)} 条数据")

# 主函数
def main():
    """
    主函数，执行整个流程
    """
    print("开始生成种子数据...")
    
    # 初始化数据库
    init_db()
    
    # 生成数据
    data = generate_seed_data()
    print(f"生成了 {len(data)} 条数据")
    
    # 插入数据
    insert_data(data)
    
    print("种子数据生成完成！")

if __name__ == "__main__":
    main()
