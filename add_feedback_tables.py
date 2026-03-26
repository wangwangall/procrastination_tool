#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展数据库结构，添加用户反馈和行为数据表
"""

import sqlite3
import os

# 数据库路径
data_dir = 'data'
db_path = os.path.join(data_dir, 'risk_records.db')

def extend_database():
    """扩展数据库结构，添加用户反馈和行为数据表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户反馈表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        user_id INTEGER,
        feedback INTEGER, -- 1=有用, 0=没用, 2=部分有用
        comments TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (record_id) REFERENCES risk_records(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # 创建用户行为数据表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_behavior (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task_type TEXT, -- 工作/学习/生活
        time_pressure INTEGER, -- 0-100
        environment INTEGER, -- 0-100，干扰程度
        age_group TEXT,
        occupation TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # 创建使用统计表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usage_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_duration INTEGER, -- 会话时长（秒）
        actions_count INTEGER, -- 操作次数
        feature_used TEXT, -- 使用的功能
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库扩展完成！")
    print("添加了以下表：")
    print("1. user_feedback - 存储用户对建议的反馈")
    print("2. user_behavior - 存储用户行为数据")
    print("3. usage_stats - 存储使用统计数据")

if __name__ == '__main__':
    extend_database()
