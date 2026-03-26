
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime, timedelta

db_path = 'data/procrastination_notebook.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("正在查看现有记录...")

cursor.execute('SELECT id, timestamp FROM risk_records ORDER BY id')
records = cursor.fetchall()

for record in records:
    record_id, old_timestamp = record
    print(f"记录 {record_id}: {old_timestamp}")
    
    try:
        # 解析UTC时间（SQLite的CURRENT_TIMESTAMP是UTC）
        # 格式类似: '2026-03-20 12:28:00'
        if ' ' in old_timestamp:
            dt_utc = datetime.strptime(old_timestamp, '%Y-%m-%d %H:%M:%S')
        else:
            dt_utc = datetime.strptime(old_timestamp, '%Y%m%d%H%M%S')
        
        # 转换为本地时间（假设中国时区 UTC+8）
        dt_local = dt_utc + timedelta(hours=8)
        
        # 格式化时间
        new_timestamp = dt_local.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"  -> 更新为: {new_timestamp}")
        
        # 更新
        cursor.execute('UPDATE risk_records SET timestamp = ? WHERE id = ?', 
                      (new_timestamp, record_id))
        
    except Exception as e:
        print(f"  跳过: {e}")

conn.commit()
print("\n更新完成！")

conn.close()

