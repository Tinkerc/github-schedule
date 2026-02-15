# coding:utf-8

"""
Git操作公共模块
提供常用的Git操作函数
"""

import os
from datetime import datetime


def git_add_commit_push(date=None, filename=None):
    """
    执行git add、commit和push操作

    Args:
        date: 提交日期，如果为None则使用当前日期
        filename: 要添加的文件名，如果为None则添加所有output和script目录的文件
    """
    try:
        if filename:
            # 添加指定文件
            cmd_git_add = f'git add {filename}'
            os.system(cmd_git_add)
        else:
            # 添加output和script目录下所有文件
            cmd_git_add_output = 'git add output/*'
            cmd_git_add_script = 'git add script/*'
            os.system(cmd_git_add_output)
            os.system(cmd_git_add_script)

        # 提交并推送
        commit_date = date or datetime.now().strftime('%Y-%m-%d')
        cmd_git_commit = f'git commit -m "feat: update data {commit_date}"'
        cmd_git_push = 'git push -u origin main'

        os.system(cmd_git_commit)
        os.system(cmd_git_push)
        print(f"Files committed to Git repository")
        return True
    except Exception as e:
        print(f"Git operation failed: {str(e)}")
        return False
