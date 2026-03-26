import sqlite3
from backend.algorithm_core import get_suggestions

# 连接到数据库
conn = sqlite3.connect('data/risk_records.db')
cursor = conn.cursor()

# 获取所有记录
cursor.execute('SELECT id, risk_level FROM core_function_results')
records = cursor.fetchall()

print(f'Found {len(records)} records to update')

# 更新每条记录的建议
updated_count = 0
for record_id, risk_level in records:
    # 生成个性化建议
    suggestion = get_suggestions(risk_level)
    
    # 更新记录
    cursor.execute('UPDATE core_function_results SET suggestion = ? WHERE id = ?', (suggestion, record_id))
    updated_count += 1
    
    print(f'Updated record {record_id}: risk_level={risk_level}, suggestion={suggestion}')

# 提交并关闭连接
conn.commit()
conn.close()

print(f'Updated {updated_count} records with personalized suggestions')