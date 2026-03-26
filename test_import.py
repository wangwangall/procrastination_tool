#!/usr/bin/env python3
"""
测试app模块导入的脚本
"""

print("开始导入app模块...")
try:
    import app
    print("✅ app模块导入成功")
    print(f"app名称: {app.__name__}")
    print(f"是否有app实例: {'app' in dir(app)}")
    if hasattr(app, 'app'):
        print(f"app实例类型: {type(app.app)}")
except Exception as e:
    print(f"❌ app模块导入失败: {e}")
    import traceback
    traceback.print_exc()

print("测试完成")
