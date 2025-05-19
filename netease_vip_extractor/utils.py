#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具模块，包含通用功能
"""

import re
import os
import json
from datetime import datetime

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def normalize_song_name(name):
    """标准化歌曲名称，去除特殊字符，便于比较"""
    if not name:
        return ""
    
    # 去除括号内容和特殊字符
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\[[^\]]*\]', '', name)
    name = re.sub(r'（[^）]*）', '', name)  # 中文括号
    name = re.sub(r'【[^】]*】', '', name)  # 中文方括号
    
    # 移除常见的版本标识
    name = re.sub(r'(live|remix|cover|翻唱|现场|版|remix|纯音乐|伴奏|纯音版|完整版|片段|片段版|混音|混音版)', '', name, flags=re.IGNORECASE)
    
    # 去除特殊字符但保留中文
    name = re.sub(r'[^\w\s\u4e00-\u9fff]', '', name)
    
    # 去除多余空格并转为小写
    name = ' '.join(name.lower().split())
    
    return name.strip()


def normalize_artist_name(name):
    """标准化艺术家名称，去除特殊字符，便于比较"""
    if not name:
        return ""
    
    # 去除括号内容和特殊字符
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\[[^\]]*\]', '', name)
    name = re.sub(r'（[^）]*）', '', name)  # 中文括号
    name = re.sub(r'【[^】]*】', '', name)  # 中文方括号
    
    # 去除特殊字符但保留中文
    name = re.sub(r'[^\w\s\u4e00-\u9fff]', '', name)
    
    # 去除多余空格并转为小写
    name = ' '.join(name.lower().split())
    
    return name.strip()


def similarity(s1, s2):
    """计算两个字符串的相似度，使用Levenshtein距离"""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    
    # 计算Levenshtein距离
    len1, len2 = len(s1), len(s2)
    matrix = [[0 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
    
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j
    
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # 删除
                matrix[i][j-1] + 1,      # 插入
                matrix[i-1][j-1] + cost  # 替换
            )
    
    # 计算相似度
    distance = matrix[len1][len2]
    max_len = max(len1, len2)
    if max_len == 0:
        return 1.0
    return 1.0 - distance / max_len


def format_timestamp(timestamp):
    """将时间戳格式化为日期时间字符串"""
    if timestamp:
        try:
            return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return "未知"
    return "未知"


def format_filesize(size_bytes):
    """将字节大小格式化为MB"""
    mb_size = size_bytes / 1024 / 1024
    return f"{mb_size:.2f} MB"


def generate_timestamp():
    """生成当前时间戳字符串，用于文件名"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False


def load_config():
    """从文件加载配置"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载配置失败: {e}")
    return {}


def save_playlist_id(playlist_id):
    """保存歌单ID到配置文件"""
    config = load_config()
    config['playlist_id'] = playlist_id
    return save_config(config)


def get_playlist_id():
    """获取保存的歌单ID"""
    config = load_config()
    return config.get('playlist_id', '') 