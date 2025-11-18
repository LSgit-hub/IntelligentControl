#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
最终修复脚本
"""

import os

def fix_service_manager():
    """修复 service_manager.py 中的语法错误"""
    file_path = os.path.join(os.path.dirname(__file__), 'src', 'tools', 'service_manager.py')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 查找并修复问题行
        for i, line in enumerate(lines):
            if "for line in result.stdout.split('\n'):" in line:
                # 找到问题行，修复它
                lines[i] = "            for line in result.stdout.split('\\n'):\n"
                print(f"已修复第 {i+1} 行")
                break

        # 将修复后的内容写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print("修复完成！")
        return True

    except Exception as e:
        print(f"修复失败: {str(e)}")
        return False

def fix_all_imports():
    """修复所有导入问题"""
    # 修复 utils.logger 导入
    utils_files = [
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'system_tools.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'interpreter_tools.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'file_manager.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'file_search.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'file_comparator.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'command_executor.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'process_manager.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'service_manager.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'registry.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'system_info.py'),
        os.path.join(os.path.dirname(__file__), 'src', 'tools', 'performance_monitor.py')
    ]

    for file_path in utils_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 修复导入语句
                content = content.replace('from utils.logger import setup_logger', 'from src.utils.logger import setup_logger')

                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"已修复: {file_path}")
            except Exception as e:
                print(f"修复失败: {file_path} - {str(e)}")

if __name__ == "__main__":
    print("开始最终修复...")
    fix_service_manager()
    fix_all_imports()
    print("修复完成！")
