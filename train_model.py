#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
训练拖延风险预测模型
使用逻辑回归算法训练二分类模型
"""

import sqlite3
import os
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 数据库路径
db_path = 'data/risk_records.db'

# 加载数据
def load_data():
    """
    从数据库加载训练数据
    
    Returns:
        X: 特征数据（task_aversion, result_value, self_control）
        y: 标签数据（actual_delay）
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 读取数据
    cursor.execute("SELECT task_aversion, result_value, self_control, actual_delay FROM risk_records")
    data = cursor.fetchall()
    
    conn.close()
    
    # 分离特征和标签
    X = []
    y = []
    for row in data:
        X.append([row[0], row[1], row[2]])
        y.append(row[3])
    
    return X, y

# 训练模型
def train_model(X, y):
    """
    训练逻辑回归模型
    
    Args:
        X: 特征数据
        y: 标签数据
    
    Returns:
        model: 训练好的模型
        accuracy: 训练集准确率
    """
    # 分割训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 创建并训练模型
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # 计算准确率
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return model, accuracy

# 保存模型
def save_model(model, filename='model.pkl'):
    """
    保存模型到文件
    
    Args:
        model: 训练好的模型
        filename: 保存文件名
    """
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"模型已保存为 {filename}")

# 主函数
def main():
    """
    主函数，执行整个训练流程
    """
    print("开始加载数据...")
    X, y = load_data()
    print(f"加载了 {len(X)} 条数据")
    
    print("开始训练模型...")
    model, accuracy = train_model(X, y)
    print(f"训练集准确率: {accuracy:.4f}")
    
    print("保存模型...")
    save_model(model)
    
    print("模型训练完成！")

if __name__ == "__main__":
    main()
