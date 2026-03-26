#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查种子数据是否正确插入
"""

import sqlite3

# 连接数据库
db_path = 'data/risk_records.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看表结构
print("表结构:")
cursor.execute("PRAGMA table_info(risk_records)")
columns = cursor.fetchall()
for column in columns:
    print(f"列名: {column[1]}, 类型: {column[2]}")

# 查看数据数量
cursor.execute("SELECT COUNT(*) FROM risk_records")
count = cursor.fetchone()[0]
print(f"\n数据总数: {count}")

# 查看各场景的数据分布
print("\n各场景的数据分布:")
cursor.execute("SELECT source, COUNT(*) FROM risk_records GROUP BY source")
scenario_counts = cursor.fetchall()
for scenario, count in scenario_counts:
    print(f"{scenario}: {count} 条")

# 查看拖延情况分布
print("\n拖延情况分布:")
cursor.execute("SELECT actual_delay, COUNT(*) FROM risk_records GROUP BY actual_delay")
delay_counts = cursor.fetchall()
for delay, count in delay_counts:
    status = "拖延" if delay == 1 else "不拖延"
    print(f"{status}: {count} 条")

# 查看前5条数据
print("\n前5条数据:")
cursor.execute("SELECT * FROM risk_records LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 关闭连接
conn.close()
