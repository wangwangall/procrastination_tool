import sqlite3
import os

# 检查数据库中所有历史记录
def check_all_history():
    print("=== 检查数据库中所有历史记录 ===")
    
    # 数据库路径
    data_dir = 'data'
    db_path = os.path.join(data_dir, 'risk_records.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("1. 检查core_function_results表中的记录:")
    # 统计总记录数
    cursor.execute("SELECT COUNT(*) FROM core_function_results")
    total = cursor.fetchone()[0]
    print(f"   总记录数: {total}")
    
    # 按匿名ID分组统计
    cursor.execute("SELECT anonymous_id, COUNT(*) as count FROM core_function_results GROUP BY anonymous_id ORDER BY count DESC")
    user_counts = cursor.fetchall()
    print(f"   不同用户数量: {len(user_counts)}")
    
    print("   各用户记录数:")
    for anonymous_id, count in user_counts[:10]:
        print(f"   - {anonymous_id}: {count}条")
    
    print("\n2. 检查risk_records表中的记录:")
    # 统计总记录数
    cursor.execute("SELECT COUNT(*) FROM risk_records")
    total_old = cursor.fetchone()[0]
    print(f"   总记录数: {total_old}")
    
    # 检查test_user_123的记录
    print("\n3. 检查test_user_123的记录:")
    cursor.execute("SELECT COUNT(*) FROM core_function_results WHERE anonymous_id = 'test_user_123'")
    test_user_count = cursor.fetchone()[0]
    print(f"   core_function_results表中test_user_123的记录数: {test_user_count}")
    
    # 查看test_user_123的最新5条记录
    cursor.execute("SELECT timestamp, score, risk_level FROM core_function_results WHERE anonymous_id = 'test_user_123' ORDER BY timestamp DESC LIMIT 5")
    test_user_records = cursor.fetchall()
    print("   最新5条记录:")
    for record in test_user_records:
        print(f"   - {record[0]}: 分数{record[1]:.1f}, {record[2]}风险")
    
    # 检查数据库索引
    print("\n4. 检查core_function_results表的索引:")
    cursor.execute("PRAGMA index_list(core_function_results)")
    indexes = cursor.fetchall()
    print(f"   索引数量: {len(indexes)}")
    for index in indexes:
        print(f"   - {index[1]}: {index[2]}")
    
    conn.close()
    
    print("\n=== 检查完成 ===")
    print(f"结论: core_function_results表中有{total}条记录，分布在{len(user_counts)}个用户中")

if __name__ == "__main__":
    check_all_history()
