import sqlite3
import random
from datetime import datetime, timedelta

# 连接到数据库
conn = sqlite3.connect('data/risk_records.db')
cursor = conn.cursor()

# 生成匿名用户
anonymous_id = 'test_user_123'
cursor.execute('INSERT OR IGNORE INTO anonymous_users (anonymous_id) VALUES (?)', (anonymous_id,))

# 生成测试数据
test_records = []
for i in range(5):
    # 随机生成评估数据
    task_aversion = random.randint(20, 80)
    result_value = random.randint(20, 80)
    self_control = random.randint(20, 80)
    
    # 随机生成权重
    w1 = round(random.uniform(0.2, 0.6), 1)
    w2 = round(random.uniform(0.2, 0.6), 1)
    w3 = round(1.0 - w1 - w2, 1)  # 确保权重和为1
    
    # 计算分数和风险等级
    score = task_aversion * w1 + (100 - result_value) * w2 + (100 - self_control) * w3
    if score < 30:
        risk_level = '低'
    elif score < 70:
        risk_level = '中'
    else:
        risk_level = '高'
    
    # 随机生成模型预测
    model_predictions = ['低', '中', '高']
    model_prediction = random.choice(model_predictions)
    
    # 对比结果
    comparison = '一致' if model_prediction == risk_level else '不一致'
    
    # 生成建议
    suggestions = {
        '低': '你目前的拖延风险较低，继续保持良好的工作习惯。',
        '中': '你的拖延风险中等，建议尝试一些时间管理技巧。',
        '高': '你的拖延风险较高，建议寻求专业帮助或使用时间管理工具。'
    }
    suggestion = suggestions[risk_level]
    
    # 生成时间戳
    timestamp = (datetime.now() - timedelta(days=i)).isoformat()
    
    # 添加到测试数据
    test_records.append((
        anonymous_id, task_aversion, result_value, self_control,
        w1, w2, w3, score, risk_level, model_prediction, comparison, suggestion, timestamp
    ))

# 插入测试数据到core_function_results表
sql = '''
INSERT INTO core_function_results (
    anonymous_id, task_aversion, result_value, self_control,
    w1, w2, w3, score, risk_level, model_prediction, comparison, suggestion, timestamp
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''
cursor.executemany(sql, test_records)

# 提交并关闭连接
conn.commit()
conn.close()

print(f'成功生成 {len(test_records)} 条测试记录')