#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加用户表到数据库
"""

import sqlite3

def add_user_table():
    """
    添加用户表到数据库
    """
    try:
        # 连接数据库
        conn = sqlite3.connect('data/risk_records.db')
        c = conn.cursor()
        
        # 创建用户表
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 修改risk_records表，添加user_id字段
        try:
            c.execute('ALTER TABLE risk_records ADD COLUMN user_id INTEGER')
            print("成功添加user_id字段到risk_records表")
        except sqlite3.OperationalError:
            print("user_id字段已存在，跳过")
        
        # 提交更改
        conn.commit()
        print("成功创建用户表")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_user_table()
