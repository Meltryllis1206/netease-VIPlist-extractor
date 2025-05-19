#!/bin/bash
# 网易云音乐VIP歌曲提取工具启动脚本

echo "====================================================="
echo "          网易云音乐VIP歌曲提取工具"
echo "====================================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    echo "请安装Python 3.6或更高版本后再运行此脚本"
    echo "您可以从 https://www.python.org/downloads/ 下载Python"
    echo ""
    echo "按回车键退出..."
    read
    exit 1
fi

# 运行提取工具
python3 extract_vip.py

# 脚本结束
exit 0 