#!/usr/bin/env python3
"""
简单测试app.py前半部分的脚本
"""

print("开始测试app.py前半部分...")

# 尝试直接读取app.py文件，只执行前100行
with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 只保留前100行
short_content = "".join(lines[:100])

# 写入临时文件
with open("temp_app.py", "w", encoding="utf-8") as f:
    f.write(short_content)

print("已创建temp_app.py文件，包含app.py的前100行")

# 尝试导入临时文件
try:
    print("尝试导入temp_app.py...")
    import temp_app
    print("✅ temp_app.py导入成功")
except Exception as e:
    print(f"❌ temp_app.py导入失败: {e}")
    import traceback
    traceback.print_exc()

# 清理临时文件
import os
os.remove("temp_app.py")
print("已清理temp_app.py文件")
print("测试完成")
