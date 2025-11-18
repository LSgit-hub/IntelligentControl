#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量修复导入语句脚本
"""

import os
import re

def fix_imports_in_file(file_path):
    """
    修复单个文件中的导入语句

    参数:
        file_path: 文件路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找并修复导入语句
        pattern = r'from (utils|tools|ai_interface|ui|tests|config)\. import'
        replacement_map = {
            'utils': 'src.utils',
            'tools': 'src.tools',
            'ai_interface': 'src.ai_interface',
            'ui': 'src.ui',
            'tests': 'src.tests',
            'config': 'src.config'
        }

        def replace_import(match):
            module = match.group(1)
            return f"from {replacement_map[module]} import"

        new_content = re.sub(pattern, replace_import, content)

        # 查找并修复点导入语句
        dot_pattern = r'from \.\. import'
        new_content = re.sub(dot_pattern, 'from src import', new_content)

        # 查找并修复相对导入
        rel_pattern = r'from \.\.(\w+) import'
        def replace_rel_import(match):
            return f"from src.{match.group(1)} import"

        new_content = re.sub(rel_pattern, replace_rel_import, new_content)

        # 查找并修复单个点导入
        single_dot_pattern = r'from \. import'
        new_content = re.sub(single_dot_pattern, 'from src import', new_content)

        # 如果内容有变化，则写入文件
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已修复: {file_path}")
            return True
        else:
            print(f"无需修复: {file_path}")
            return False

    except Exception as e:
        print(f"修复失败: {file_path} - {str(e)}")
        return False

def fix_imports_in_directory(directory):
    """
    修复目录中的所有Python文件的导入语句

    参数:
        directory: 目录路径
    """
    fixed_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    fixed_count += 1

    print(f"总共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    # 修复src目录中的所有Python文件
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    fix_imports_in_directory(src_dir)

    print("导入修复完成！")
