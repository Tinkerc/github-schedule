import os
import sys
import importlib.util
from datetime import datetime
from dotenv import load_dotenv
from script.utils.git_helper import git_add_commit_push

# 加载 .env 文件中的环境变量
load_dotenv()

def load_and_execute_script(script_path):
    try:
        # 获取脚本文件名（不含路径和扩展名）
        script_name = os.path.splitext(os.path.basename(script_path))[0]
        
        # 加载脚本模块
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 执行脚本的job函数
        if hasattr(module, 'job'):
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行脚本: {script_path}")
            module.job()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 脚本执行完成: {script_path}")
            return True
        else:
            print(f"警告: {script_path} 中没有找到job函数，跳过执行")
            return False
    except Exception as e:
        print(f"错误: 执行脚本 {script_path} 时发生异常: {str(e)}")
        return False

def main():
    # 获取script目录的绝对路径
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'script')
    
    if not os.path.exists(script_dir):
        print(f"错误: 目录 {script_dir} 不存在")
        sys.exit(1)
    
    # 获取所有.py文件并按文件名排序
    python_files = sorted([f for f in os.listdir(script_dir) if f.endswith('.py')])
    
    if not python_files:
        print(f"警告: 在 {script_dir} 目录下没有找到Python脚本")
        sys.exit(0)
    
    print(f"找到 {len(python_files)} 个Python脚本，按以下顺序执行:")
    for i, file in enumerate(python_files, 1):
        print(f"{i}. {file}")
    
    # 执行统计
    success_count = 0
    failed_count = 0
    
    # 按顺序执行每个脚本
    for python_file in python_files:
        script_path = os.path.join(script_dir, python_file)
        if load_and_execute_script(script_path):
            success_count += 1
        else:
            failed_count += 1
    #submit to github
    #git_add_commit_push()

    # 输出执行统计结果
    print(f"\n执行统计:")
    print(f"总计脚本数: {len(python_files)}")
    print(f"成功执行: {success_count}")
    print(f"执行失败: {failed_count}")

if __name__ == '__main__':
    main()