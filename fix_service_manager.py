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
            content = f.read()

        # 修复未闭合的字符串
        old_text = "for line in result.stdout.split('"
        new_text = "for line in result.stdout.split('\\n')"

        if old_text in content:
            content = content.replace(old_text, new_text)
            print("已修复 service_manager.py 中的字符串错误")
        else:
            print("未找到需要修复的字符串错误")

        # 修复转义字符警告
        old_text = '"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"'
        new_text = r'"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"'

        if old_text in content:
            content = content.replace(old_text, new_text)
            print("已修复转义字符警告")

        # 将修复后的内容写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("修复完成！")
        return True

    except Exception as e:
        print(f"修复失败: {str(e)}")
        return False

if __name__ == "__main__":
    fix_service_manager()
