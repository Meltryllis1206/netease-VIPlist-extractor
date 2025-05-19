#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
云盘音乐模块，用于获取和处理云盘音乐列表
"""

import os
import json
import requests
from datetime import datetime
from crypto_utils import encrypted_request
from utils import normalize_song_name, normalize_artist_name, format_timestamp, format_filesize, generate_timestamp

# API地址
BASE_URL = "https://music.163.com"
CLOUD_MUSIC_URL = BASE_URL + "/weapi/v1/cloud/get"
SONG_DETAIL_URL = BASE_URL + "/weapi/v3/song/detail"

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://music.163.com/',
    'Content-Type': 'application/x-www-form-urlencoded',
}

# Cookie文件路径
COOKIE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookie.json")


def get_cloud_music(limit=1000, offset=0, cookies=None):
    """获取用户云盘音乐列表"""
    data = {
        'limit': limit,
        'offset': offset,
        'csrf_token': ''
    }
    
    if cookies is None:
        cookies = get_cookies()
        
    response = requests.post(CLOUD_MUSIC_URL, data=encrypted_request(data), headers=HEADERS, cookies=cookies)
    result = response.json()
    
    if result.get('code') == 200:
        return result.get('data', [])
    return []


def get_all_cloud_music(cookies=None):
    """获取所有云盘音乐"""
    all_cloud_music = []
    limit = 1000
    offset = 0
    
    if cookies is None:
        cookies = get_cookies()
    
    while True:
        data = get_cloud_music(limit, offset, cookies)
        if not data:
            break
        
        all_cloud_music.extend(data)
        
        # 如果返回的数据少于limit，说明已经获取完毕
        if len(data) < limit:
            break
        
        offset += limit
    
    return all_cloud_music


def get_song_details(song_ids, cookies=None):
    """获取歌曲详细信息"""
    if not song_ids:
        return {}
    
    if cookies is None:
        cookies = get_cookies()
    
    data = {
        'c': '[' + ','.join([f'{{"id":{song_id}}}' for song_id in song_ids]) + ']',
        'ids': '[' + ','.join([str(song_id) for song_id in song_ids]) + ']',
        'csrf_token': ''
    }
    
    response = requests.post(SONG_DETAIL_URL, data=encrypted_request(data), headers=HEADERS, cookies=cookies)
    result = response.json()
    
    if result.get('code') == 200:
        songs = result.get('songs', [])
        return {song['id']: song for song in songs}
    
    return {}


def save_cookies(cookies):
    """保存Cookie到文件"""
    try:
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
        return True
    except Exception as e:
        print(f"保存Cookie失败: {e}")
        return False


def load_cookies():
    """从文件加载Cookie"""
    try:
        if os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载Cookie失败: {e}")
    return None


def get_cookies():
    """获取用户登录后的Cookie"""
    # 先尝试从文件加载Cookie
    cookies = load_cookies()
    if cookies:
        print("已从文件加载Cookie")
        return cookies
    
    # 如果文件不存在或加载失败，则提示用户输入
    cookies_str = input("请输入网易云音乐登录后的Cookie（可从浏览器开发者工具中获取）: ")
    
    # 解析Cookie字符串为字典
    cookies = {}
    if cookies_str:
        for item in cookies_str.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
        
        # 保存Cookie到文件
        save_cookies(cookies)
    
    return cookies


def save_cloud_music_to_markdown(cloud_music_info):
    """将云盘音乐列表保存为Markdown文件"""
    timestamp = generate_timestamp()
    filename = f"云盘音乐列表_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 网易云音乐云盘音乐列表\n\n")
        f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总计: {len(cloud_music_info)} 首歌曲\n\n")
        
        f.write("| 序号 | 原始歌曲名称 | 原始艺术家 | 匹配歌曲名称 | 匹配艺术家 | 文件大小 | 添加时间 |\n")
        f.write("|------|------------|----------|------------|----------|---------|--------|\n")
        
        for i, song in enumerate(cloud_music_info, 1):
            # 原始信息
            original_name = song.get('name', '')
            original_artist = song.get('artist', '')
            
            # 匹配信息
            matched_name = song.get('matched_name', '') or original_name
            matched_artist = song.get('matched_artist', '') or original_artist
            
            # 格式化信息
            file_size_str = format_filesize(song.get('fileSize', 0))
            add_time_str = format_timestamp(song.get('addTime', 0))
            
            f.write(f"| {i} | {original_name} | {original_artist} | {matched_name} | {matched_artist} | {file_size_str} | {add_time_str} |\n")
    
    print(f"已将{len(cloud_music_info)}首云盘音乐信息保存到文件: {filename}")
    return filename


def extract_cloud_music_info(cookies=None):
    """提取云盘音乐信息"""
    print("正在获取云盘音乐列表...")
    
    if cookies is None:
        cookies = get_cookies()
        
    cloud_music_list = get_all_cloud_music(cookies)
    
    print(f"共找到 {len(cloud_music_list)} 首云盘音乐")
    
    # 收集所有已匹配的歌曲ID
    song_ids = []
    for item in cloud_music_list:
        # 检查是否有匹配的歌曲ID
        if 'songId' in item and item['songId']:
            song_ids.append(item['songId'])
    
    # 获取歌曲详细信息
    print("正在获取匹配的歌曲详细信息...")
    song_details = get_song_details(song_ids, cookies)
    print(f"成功获取 {len(song_details)} 首匹配歌曲的详细信息")
    
    # 提取歌曲信息
    cloud_music_info = []
    for item in cloud_music_list:
        song_name = item.get('songName', '')
        artist_name = item.get('artist', '')
        
        # 标准化歌曲名称和艺术家名称
        normalized_name = normalize_song_name(song_name)
        normalized_artist = normalize_artist_name(artist_name)
        
        # 获取匹配的歌曲信息
        matched_name = ""
        matched_artist = ""
        if 'songId' in item and item['songId'] and item['songId'] in song_details:
            song_detail = song_details[item['songId']]
            matched_name = song_detail.get('name', '')
            artists = song_detail.get('ar', [])
            # 安全处理艺术家列表，过滤掉None值
            if artists:
                artist_names = [artist.get('name', '') for artist in artists if artist is not None and artist.get('name') is not None]
                matched_artist = ', '.join(artist_names)
        
        cloud_music_info.append({
            'name': song_name,
            'artist': artist_name,
            'normalized_name': normalized_name,
            'normalized_artist': normalized_artist,
            'matched_name': matched_name,
            'matched_artist': matched_artist,
            'fileSize': item.get('fileSize', 0),
            'addTime': item.get('addTime', 0),
            'songId': item.get('songId', 0)
        })
    
    return cloud_music_info


if __name__ == "__main__":
    cloud_music_info = extract_cloud_music_info()
    # 保存云盘音乐列表到Markdown文件
    if cloud_music_info:
        save_cloud_music_to_markdown(cloud_music_info)
    
    print(f"云盘音乐列表：")
    for i, song in enumerate(cloud_music_info, 1):
        matched_info = f" (匹配: {song['matched_name']} - {song['matched_artist']})" if song['matched_name'] else ""
        print(f"{i}. {song['name']} - {song['artist']}{matched_info}") 