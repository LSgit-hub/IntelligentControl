#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全面修复导入语句脚本
"""

import os
import re

def fix_file_imports(file_path):
    """修复单个文件中的导入语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 修复所有 utils.logger 导入
        content = content.replace('from utils.logger import setup_logger', 'from src.utils.logger import setup_logger')

        # 修复所有其他 utils 导入
        content = content.replace('from utils import', 'from src.utils import')

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"已修复: {file_path}")
        return True
    except Exception as e:
        print(f"修复失败: {file_path} - {str(e)}")
        return False

def fix_all_files():
    """修复所有工具文件"""
    tools_dir = os.path.join(os.path.dirname(__file__), 'src', 'tools')

    for file in os.listdir(tools_dir):
        if file.endswith('.py'):
            file_path = os.path.join(tools_dir, file)
            fix_file_imports(file_path)

    # 修复其他可能需要修复的文件
    other_files = [
        os.path.join(os.path.dirname(__file__), 'src', 'core', 'app.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'core', 'command_handler.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'core', 'dialog_manager.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'ai_interface', 'ai_manager.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'ai_interface', 'lmstudio.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'config', 'settings.py')
    ]

    for file_path in other_files:
        if os.path.exists(file_path):
            fix_file_imports(file_path)

if __name__ == "__main__":
    print("开始全面修复导入语句...")
    fix_all_files()
    print("修复完成！")
