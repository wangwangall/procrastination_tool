#!/usr/bin/env python3
# coding: utf-8

import sqlite3
import os

# 数据库路径
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
db_path = os.path.join(data_dir, 'risk_records.db')

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 添加model_prediction列
try:
    cursor.execute('ALTER TABLE core_function_results ADD COLUMN model_prediction TEXT NOT NULL DEFAULT "中等"')
    conn.commit()
    print("✓ 添加model_prediction列成功")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("model_prediction列已存在")
    else:
        print(f"添加model_prediction列失败: {e}")

# 添加comparison列
try:
    cursor.execute('ALTER TABLE core_function_results ADD COLUMN comparison TEXT NOT NULL DEFAULT "一致"')
    conn.commit()
    print("✓ 添加comparison列成功")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("comparison列已存在")
    else:
        print(f"添加comparison列失败: {e}")

# 添加suggestion列
try:
    cursor.execute('ALTER TABLE core_function_results ADD COLUMN suggestion TEXT NOT NULL DEFAULT "根据你的评估结果，我们建议你采取适合自己的方法来管理拖延问题。"')
    conn.commit()
    print("✓ 添加suggestion列成功")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("suggestion列已存在")
    else:
        print(f"添加suggestion列失败: {e}")

# 关闭数据库连接
conn.close()
print("数据库表结构更新完成！")
