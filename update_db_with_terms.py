#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新数据库，添加协议同意相关字段
"""

import sqlite3
import os

# 数据库路径
db_path = 'data/procrastination_notebook.db'

def update_database():
    """更新数据库表结构，添加协议同意字段"""
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("开始更新数据库表结构...")
        
        # 检查users表是否已经有agreed_to_terms字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 如果没有agreed_to_terms字段，添加它
        if 'agreed_to_terms' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN agreed_to_terms INTEGER DEFAULT 0")
            print("添加字段: agreed_to_terms")
        
        # 如果没有terms_agreed_at字段，添加它
        if 'terms_agreed_at' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN terms_agreed_at TEXT")
            print("添加字段: terms_agreed_at")
        
        # 提交更改
        conn.commit()
        print("数据库更新成功！")
        
    except Exception as e:
        print(f"数据库更新失败: {e}")
    finally:
        # 关闭数据库连接
        conn.close()

if __name__ == "__main__":
    update_database()