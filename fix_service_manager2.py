#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复 service_manager.py 中的字符串错误
"""

import os

def fix_service_manager():
    """修复 service_manager.py 中的字符串错误"""
    file_path = os.path.join(os.path.dirname(__file__), 'src', 'tools', 'service_manager.py')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 查找并修复问题行
        for i, line in enumerate(lines):
            if "for line in result.stdout.split('\\\\n')" in line and i < len(lines)-1 and lines[i+1].strip() == "'):
                # 修复这两行
                lines[i] = "            for line in result.stdout.split('\\\\n'):\n"
                del lines[i+1]
                print(f"已修复第 {i+1} 行和第 {i+2} 行的字符串错误")
                break

        # 将修复后的内容写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print("修复完成！")
        return True

    except Exception as e:
        print(f"修复失败: {str(e)}")
        return False

if __name__ == "__main__":
    fix_service_manager()
