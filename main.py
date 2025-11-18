#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能控制助手主程序入口
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.app import main

if __name__ == "__main__":
    main()
