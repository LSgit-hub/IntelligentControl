#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导入修复脚本
用于修复项目中的模块导入问题
"""

import os
import sys
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

        # 匹配导入语句
        import_pattern = re.compile(r'from (utils|tools|ai_interface|ui|tests|config)\. import')

        # 替换导入语句
        def replace_import(match):
            module = match.group(1)
            if module == 'utils':
                return f'from ..{module} import'
            elif module in ['tools', 'ai_interface', 'ui', 'tests', 'config']:
                return f'from ..{module} import'
            else:
                return match.group(0)

        new_content = import_pattern.sub(replace_import, content)

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

    # 修复根目录中的Python文件
    for file in os.listdir(os.path.dirname(__file__)):
        if file.endswith('.py') and file != 'fix_imports.py':
            fix_imports_in_file(os.path.join(os.path.dirname(__file__), file))

    print("导入修复完成！")
