#!/usr/bin/env python3
"""
更新数据库结构，支持匿名ID多用户模式
"""

import sqlite3
import os

def update_database():
    """更新数据库结构"""
    # 确保data目录存在
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 数据库路径
    db_path = os.path.join(data_dir, 'risk_records.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("开始更新数据库结构...")
    
    # 1. 创建anonymous_users表，存储匿名用户信息和自定义权重
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anonymous_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anonymous_id TEXT UNIQUE NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        w1 REAL DEFAULT 0.4,
        w2 REAL DEFAULT 0.3,
        w3 REAL DEFAULT 0.3
    )
    ''')
    print("✓ 创建anonymous_users表")
    
    # 2. 创建core_function_results表，存储核心函数结果
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS core_function_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anonymous_id TEXT NOT NULL,
        task_aversion INTEGER NOT NULL,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        user_notes TEXT
    )
    ''')
    print("✓ 创建core_function_results表")
    
    # 3. 创建model_predictions表，存储模型预测结果
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS model_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anonymous_id TEXT NOT NULL,
        task_aversion INTEGER NOT NULL,
        result_value INTEGER NOT NULL,
        self_control INTEGER NOT NULL,
        w1 REAL NOT NULL,
        w2 REAL NOT NULL,
        w3 REAL NOT NULL,
        predicted_level TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ 创建model_predictions表")
    
    # 4. 修改risk_records表，添加anonymous_id字段
    cursor.execute('PRAGMA table_info(risk_records)')
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'anonymous_id' not in columns:
        cursor.execute('ALTER TABLE risk_records ADD COLUMN anonymous_id TEXT')
        print("✓ 修改risk_records表，添加anonymous_id字段")
    
    # 5. 修改user_feedback表，添加anonymous_id字段
    cursor.execute('PRAGMA table_info(user_feedback)')
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'anonymous_id' not in columns:
        cursor.execute('ALTER TABLE user_feedback ADD COLUMN anonymous_id TEXT')
        print("✓ 修改user_feedback表，添加anonymous_id字段")
    
    # 6. 修改user_behavior表，添加anonymous_id字段
    cursor.execute('PRAGMA table_info(user_behavior)')
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'anonymous_id' not in columns:
        cursor.execute('ALTER TABLE user_behavior ADD COLUMN anonymous_id TEXT')
        print("✓ 修改user_behavior表，添加anonymous_id字段")
    
    # 7. 修改usage_stats表，添加anonymous_id字段
    cursor.execute('PRAGMA table_info(usage_stats)')
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'anonymous_id' not in columns:
        cursor.execute('ALTER TABLE usage_stats ADD COLUMN anonymous_id TEXT')
        print("✓ 修改usage_stats表，添加anonymous_id字段")
    
    # 提交更改
    conn.commit()
    
    # 关闭连接
    conn.close()
    
    print("\n🎉 数据库结构更新完成！")
    print("\n新创建的表：")
    print("- anonymous_users: 存储匿名用户信息和自定义权重")
    print("- core_function_results: 存储核心函数结果")
    print("- model_predictions: 存储模型预测结果")
    print("\n已修改的表：")
    print("- risk_records: 添加了anonymous_id字段")
    print("- user_feedback: 添加了anonymous_id字段")
    print("- user_behavior: 添加了anonymous_id字段")
    print("- usage_stats: 添加了anonymous_id字段")

if __name__ == "__main__":
    update_database()
