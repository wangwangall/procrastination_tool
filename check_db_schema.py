import sqlite3

# 连接到数据库
conn = sqlite3.connect('data/risk_records.db')
cursor = conn.cursor()

# 查看 core_function_results 表的结构
print('Structure of core_function_results table:')
cursor.execute('PRAGMA table_info(core_function_results);')
columns = cursor.fetchall()
for column in columns:
    print(f'  {column[1]} ({column[2]}) - NOT NULL: {column[3]}, Default: {column[4]}')

# 关闭连接
conn.close()