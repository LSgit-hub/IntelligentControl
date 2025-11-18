#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
语法错误修复脚本
用于修复command_handler.py中的语法错误
"""

import os

def fix_command_handler():
    """修复command_handler.py中的语法错误"""
    file_path = os.path.join(os.path.dirname(__file__), 'src', 'core', 'command_handler.py')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 查找并修复第1271行（索引1270）的语法错误
        for i, line in enumerate(lines):
            if "console.print(f\"[bold green]AI响应\"" in line and \"result.get('model', '')\" in line:
                # 找到问题行，修复它
                original_line = line
                # 修复未闭合的字符串
                fixed_line = line.replace(
                    "result.get('model', '')", 
                    "result.get('model', '')"
                )

                if original_line != fixed_line:
                    lines[i] = fixed_line
                    print(f"修复了第 {i+1} 行的语法错误")
                    break

        # 将修复后的内容写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print("语法错误修复完成！")
        return True

    except Exception as e:
        print(f"修复失败: {str(e)}")
        return False

if __name__ == "__main__":
    fix_command_handler()
