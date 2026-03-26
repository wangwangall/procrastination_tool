import pickle
import os
import numpy as np

# 模型文件路径
model_path = 'model.pkl'

if os.path.exists(model_path):
    print("模型文件存在，正在加载...")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("模型加载成功!")
    print(f"模型类型: {type(model)}")
    print(f"模型内容: {model}")
    
    # 检查模型是否有训练数据的痕迹
    try:
        if hasattr(model, 'coef_'):
            print(f"模型系数: {model.coef_}")
            print(f"模型截距: {model.intercept_}")
            print("模型已经过训练！")
        else:
            print("模型尚未训练")
    except Exception as e:
        print(f"检查模型训练状态失败: {e}")
        print("模型可能不是scikit-learn模型或训练不完整")
else:
    print("模型文件不存在!")