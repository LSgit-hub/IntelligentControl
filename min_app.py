#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
最小化应用程序启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入必要的模块
try:
    from src.core.app import main
    main()
except Exception as e:
    print(f"启动失败: {str(e)}")
    print("请检查所有导入语句是否正确")
