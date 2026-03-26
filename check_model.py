import pickle
import os

# 模型文件路径
model_path = 'model.pkl'

if os.path.exists(model_path):
    print("模型文件存在，正在加载...")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("模型加载成功!")
    print(f"模型类型: {type(model)}")
    print(f"模型内容: {model}")
else:
    print("模型文件不存在!")