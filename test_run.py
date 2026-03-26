#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import app

# 配置详细的日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

try:
    logging.info("尝试启动应用...")
    # 使用flask的run方法启动应用
    app.app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    logging.info("应用启动成功")
except Exception as e:
    logging.error(f"应用启动失败: {str(e)}")
    import traceback
    traceback.print_exc()