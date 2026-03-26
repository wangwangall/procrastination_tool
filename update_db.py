import sqlite3
import os

# 确保data目录存在
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

db_path = os.path.join(data_dir, 'risk_records.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 检查字段是否已存在
    cursor.execute("PRAGMA table_info(risk_records)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'delay_probability' not in columns:
        # 添加delay_probability字段
        cursor.execute('ALTER TABLE risk_records ADD COLUMN delay_probability REAL')
        conn.commit()
        print('成功添加delay_probability字段')
    else:
        print('delay_probability字段已存在')
except Exception as e:
    print(f'操作失败: {e}')
finally:
    conn.close()