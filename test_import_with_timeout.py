#!/usr/bin/env python3
"""
带有超时机制的app模块导入测试脚本
"""

import sys
import os
import threading
import time

# 设置导入超时时间（秒）
IMPORT_TIMEOUT = 5

# 用于保存导入结果
import_result = None
import_exception = None


def import_app():
    """在单独的线程中导入app模块"""
    global import_result, import_exception
    try:
        print("线程中开始导入app模块...")
        # 确保当前目录在Python路径中
        sys.path.insert(0, os.getcwd())
        import app
        import_result = app
        print("线程中app模块导入成功")
    except Exception as e:
        import_exception = e
        print(f"线程中app模块导入失败: {e}")


print(f"开始测试app模块导入，超时时间: {IMPORT_TIMEOUT}秒")

# 创建并启动导入线程
import_thread = threading.Thread(target=import_app)
import_thread.daemon = True
import_thread.start()

# 等待导入完成或超时
start_time = time.time()
while import_result is None and import_exception is None:
    elapsed_time = time.time() - start_time
    if elapsed_time > IMPORT_TIMEOUT:
        print(f"❌ 导入超时，耗时: {elapsed_time:.1f}秒")
        break
    time.sleep(0.1)

# 打印导入结果
if import_result is not None:
    print(f"✅ app模块导入成功，耗时: {time.time() - start_time:.1f}秒")
    print(f"app模块名称: {import_result.__name__}")
    print(f"是否有app实例: {'app' in dir(import_result)}")
    if hasattr(import_result, 'app'):
        print(f"app实例类型: {type(import_result.app)}")
elif import_exception is not None:
    print(f"❌ app模块导入失败，耗时: {time.time() - start_time:.1f}秒")
    print(f"错误信息: {import_exception}")
    import traceback
    traceback.print_exc()
else:
    print("❌ 导入超时，未知错误")

print("测试完成")
