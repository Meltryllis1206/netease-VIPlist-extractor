#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐VIP歌曲提取工具 - 启动脚本
这个脚本用于从项目根目录启动提取工具
"""

import os
import sys
import subprocess
import platform
import time

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("          网易云音乐VIP歌曲提取工具")
    print("=" * 60)
    print("这个工具可以帮助你找出网易云音乐歌单中的VIP歌曲，")
    print("并与你的云盘音乐进行比对，找出哪些VIP歌曲是你还没有的。")
    print("=" * 60)
    print()

def get_playlist_id_from_config(current_dir):
    """从配置文件获取歌单ID"""
    config_path = os.path.join(current_dir, "config.json")
    if os.path.exists(config_path):
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('playlist_id')
        except:
            return None
    return None

def main():
    # 显示欢迎信息
    print_welcome()
    
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建子目录路径
    extractor_dir = os.path.join(current_dir, "netease_vip_extractor")
    
    # 检查子目录是否存在
    if not os.path.exists(extractor_dir):
        print(f"错误: 目录 {extractor_dir} 不存在")
        print("请确保您下载了完整的工具包，并且没有修改目录结构。")
        input("按回车键退出...")
        return
    
    # 检查虚拟环境是否存在
    venv_dir = os.path.join(current_dir, "venv")
    
    # 根据操作系统确定可执行文件路径
    is_windows = platform.system() == "Windows"
    
    if is_windows:
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_bin = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_bin = os.path.join(venv_dir, "bin", "python3")
        pip_bin = os.path.join(venv_dir, "bin", "pip")
    
    if not os.path.exists(venv_dir):
        print("首次运行需要创建虚拟环境并安装依赖，这可能需要几分钟时间...")
        try:
            # 创建虚拟环境
            # 使用py命令在Windows上，或python3在其他系统上
            python_cmd = "py" if is_windows else "python3"
            print("正在创建虚拟环境...")
            subprocess.run([python_cmd, "-m", "venv", venv_dir], check=True)
            
            # 安装依赖
            requirements_path = os.path.join(extractor_dir, "requirements.txt")
            if not os.path.exists(requirements_path):
                print(f"错误: 依赖文件 {requirements_path} 不存在")
                input("按回车键退出...")
                return
            
            print("正在安装必要的依赖包...")    
            subprocess.run([pip_bin, "install", "-r", requirements_path], check=True)
            
            print("依赖安装完成！")
        except subprocess.CalledProcessError as e:
            print(f"环境设置失败: {e}")
            print("请尝试手动安装依赖包：")
            print(f"1. 打开命令提示符")
            print(f"2. 执行: pip install -r {os.path.join(extractor_dir, 'requirements.txt')}")
            input("按回车键退出...")
            return
        except Exception as e:
            print(f"发生未知错误: {e}")
            input("按回车键退出...")
            return
    
    # 准备执行提取脚本
    extract_script = os.path.join(extractor_dir, "extract_by_id.py")
    if not os.path.exists(extract_script):
        print(f"错误: 脚本文件 {extract_script} 不存在")
        print("请确保您下载了完整的工具包。")
        input("按回车键退出...")
        return
    
    # 获取命令行参数
    args = sys.argv[1:]
    
    # 如果没有提供歌单ID，提示用户输入
    if not args:
        # 尝试从配置文件获取歌单ID
        saved_id = get_playlist_id_from_config(current_dir)
        if saved_id:
            print(f"发现上次使用的歌单ID: {saved_id}")
            print("1. 使用上次的歌单ID")
            print("2. 输入新的歌单ID")
            choice = input("请选择 (默认1): ").strip()
            if choice != "2":
                # 如果选择1或直接回车，直接使用保存的ID
                args = [saved_id]
                # 执行提取脚本
                try:
                    print("正在启动提取程序...")
                    cmd = [python_bin, extract_script] + args
                    result = subprocess.run(cmd)
                    
                    if result.returncode == 0:
                        print("\n处理完成！结果已保存到当前目录。")
                    else:
                        print("\n处理过程中出现错误，请检查上方提示信息。")
                except Exception as e:
                    print(f"执行失败: {e}")
                
                print("\n感谢使用网易云音乐VIP歌曲提取工具！")
                input("按回车键退出...")
                return
            else:
                print("\n如何获取歌单ID：")
                print("1. 打开网易云音乐APP或网页版")
                print("2. 找到你喜欢的歌单")
                print("3. 点击\"分享\"按钮")
                print("4. 复制分享链接中的数字部分")
                print("例如：链接https://music.163.com/playlist?id=123456789中，123456789就是歌单ID\n")
                print("请输入网易云音乐歌单ID: ", end="")
                playlist_id = input().strip()
                if playlist_id:
                    args = [playlist_id]
                else:
                    print("未提供歌单ID，退出")
                    input("按回车键退出...")
                    return
        else:
            print("如何获取歌单ID：")
            print("1. 打开网易云音乐APP或网页版")
            print("2. 找到你喜欢的歌单")
            print("3. 点击\"分享\"按钮")
            print("4. 复制分享链接中的数字部分")
            print("例如：链接https://music.163.com/playlist?id=123456789中，123456789就是歌单ID\n")
            print("请输入网易云音乐歌单ID: ", end="")
            playlist_id = input().strip()
            if playlist_id:
                args = [playlist_id]
            else:
                print("未提供歌单ID，退出")
                input("按回车键退出...")
                return
    
    # 执行提取脚本
    try:
        print("正在启动提取程序...")
        cmd = [python_bin, extract_script] + args
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print("\n处理完成！结果已保存到当前目录。")
        else:
            print("\n处理过程中出现错误，请检查上方提示信息。")
    except Exception as e:
        print(f"执行失败: {e}")
    
    print("\n感谢使用网易云音乐VIP歌曲提取工具！")
    input("按回车键退出...")

if __name__ == "__main__":
    main() 