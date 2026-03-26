import sqlite3

# 连接到数据库
conn = sqlite3.connect('procrastination.db')
cursor = conn.cursor()

# 检查core_function_results表的记录数
cursor.execute('SELECT COUNT(*) FROM core_function_results')
count = cursor.fetchone()[0]
print(f'Number of records in core_function_results: {count}')

# 如果有记录，显示前5条记录的基本信息
if count > 0:
    print('\nFirst 5 records:')
    cursor.execute('SELECT id, anonymous_id, score, risk_level, created_at FROM core_function_results LIMIT 5')
    records = cursor.fetchall()
    for record in records:
        print(f'ID: {record[0]}, User: {record[1]}, Score: {record[2]}, Risk: {record[3]}, Created: {record[4]}')

# 关闭连接
conn.close()