import os
import sqlite3

# 检查data目录
print('Checking data directory...')
data_dir_exists = os.path.exists('data')
print(f'Data directory exists: {data_dir_exists}')

if data_dir_exists:
    # 列出data目录内容
    print('\nContents of data directory:')
    for item in os.listdir('data'):
        print(f'  - {item}')
    
    # 检查数据库文件
    db_path = 'data/risk_records.db'
    print(f'\nDatabase file exists: {os.path.exists(db_path)}')
    
    # 如果数据库文件存在，检查其结构
    if os.path.exists(db_path):
        print('\nChecking database structure...')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f'Tables in database: {[table[0] for table in tables]}')
        
        # 检查core_function_results表的记录数
        if 'core_function_results' in [table[0] for table in tables]:
            cursor.execute('SELECT COUNT(*) FROM core_function_results')
            count = cursor.fetchone()[0]
            print(f'Number of records in core_function_results: {count}')
        
        conn.close()