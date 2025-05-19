#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网易云音乐VIP歌曲提取工具 - 主要提取脚本
"""

import json
import requests
import sys
from datetime import datetime
from crypto_utils import encrypted_request
from cloud_music import extract_cloud_music_info, save_cloud_music_to_markdown, get_cookies
from utils import normalize_song_name, normalize_artist_name, similarity, generate_timestamp
from utils import save_playlist_id, get_playlist_id

# API地址
BASE_URL = "https://music.163.com"
PLAYLIST_DETAIL_URL = BASE_URL + "/weapi/v6/playlist/detail"
SONG_DETAIL_URL = BASE_URL + "/weapi/v3/song/detail"
SONG_URL_URL = BASE_URL + "/weapi/song/enhance/player/url"

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://music.163.com/',
    'Content-Type': 'application/x-www-form-urlencoded',
}


def get_playlist_detail(playlist_id, cookies=None):
    """获取歌单详情"""
    data = {
        'id': playlist_id,
        'n': 1000,
        'csrf_token': ''
    }
    response = requests.post(PLAYLIST_DETAIL_URL, data=encrypted_request(data), headers=HEADERS, cookies=cookies)
    result = response.json()
    if result.get('code') == 200:
        playlist_name = result.get('playlist', {}).get('name', '未知歌单')
        tracks = result.get('playlist', {}).get('tracks', [])
        track_ids = [track['id'] for track in tracks]
        trackCount = result.get('playlist', {}).get('trackCount', 0)
        
        # 如果歌单中的歌曲数量大于获取到的歌曲数量，可能需要多次请求
        if trackCount > len(tracks) and 'trackIds' in result.get('playlist', {}):
            print(f"歌单中实际有 {trackCount} 首歌曲，但API只返回了 {len(tracks)} 首，将尝试获取更多...")
            all_track_ids = []
            for track_id_obj in result['playlist']['trackIds']:
                all_track_ids.append(track_id_obj['id'])
            return playlist_name, all_track_ids
        
        return playlist_name, track_ids
    return "未知歌单", []


def get_songs_detail(track_ids, cookies=None):
    """获取歌曲详情"""
    songs = []
    # 由于API限制，每次最多获取1000首歌曲，所以需要分批请求
    for i in range(0, len(track_ids), 1000):
        batch_ids = track_ids[i:i+1000]
        data = {
            'c': '[' + ','.join([f'{{"id":{track_id}}}' for track_id in batch_ids]) + ']',
            'ids': '[' + ','.join([str(track_id) for track_id in batch_ids]) + ']',
            'csrf_token': ''
        }
        response = requests.post(SONG_DETAIL_URL, data=encrypted_request(data), headers=HEADERS, cookies=cookies)
        result = response.json()
        if result.get('code') == 200:
            songs.extend(result.get('songs', []))
    return songs


def get_song_urls(track_ids, cookies=None):
    """获取歌曲URL，以判断是否需要VIP"""
    data = {
        'ids': '[' + ','.join([str(track_id) for track_id in track_ids]) + ']',
        'br': 320000,  # 比特率
        'csrf_token': ''
    }
    response = requests.post(SONG_URL_URL, data=encrypted_request(data), headers=HEADERS, cookies=cookies)
    result = response.json()
    if result.get('code') == 200:
        return {item['id']: item for item in result.get('data', [])}
    return {}


def save_to_markdown(playlist_name, vip_songs, filtered=False):
    """将VIP歌曲信息保存为Markdown文件"""
    timestamp = generate_timestamp()
    filename = f"{playlist_name}_vip_songs_{timestamp}.md"
    
    if filtered:
        filename = f"{playlist_name}_vip_songs_filtered_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {playlist_name} - VIP歌曲列表\n\n")
        f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if filtered:
            f.write("**注意：已过滤掉云盘中已有的歌曲**\n\n")
        
        f.write("| 序号 | 歌曲名称 | 艺术家 | VIP类型 |\n")
        f.write("|------|--------|--------|--------|\n")
        
        for i, song in enumerate(vip_songs, 1):
            song_name = song['name']
            artists = ', '.join([artist['name'] for artist in song['ar']])
            vip_type = song.get('vip_type', '未知')
            f.write(f"| {i} | {song_name} | {artists} | {vip_type} |\n")
    
    print(f"已将{len(vip_songs)}首VIP歌曲信息保存到文件: {filename}")
    return filename


def filter_songs_by_cloud_music(vip_songs, cloud_music_info):
    """过滤掉云盘中已有的歌曲"""
    filtered_songs = []
    removed_songs = []
    
    # 将云盘歌曲信息转换为易于查找的格式
    cloud_music_dict = {}
    cloud_music_id_dict = {}  # 按歌曲ID索引
    
    for item in cloud_music_info:
        # 优先使用匹配的歌曲信息
        if item['matched_name'] and item['matched_artist']:
            song_name = item['matched_name']
            artist_name = item['matched_artist']
        else:
            song_name = item['name']
            artist_name = item['artist']
            
        normalized_name = normalize_song_name(song_name)
        normalized_artist = normalize_artist_name(artist_name)
        
        # 记录歌曲ID，用于精确匹配
        if item['songId']:
            cloud_music_id_dict[item['songId']] = item
        
        if normalized_name:
            # 使用(歌曲名,艺术家)作为键
            key = (normalized_name, normalized_artist)
            if key not in cloud_music_dict:
                cloud_music_dict[key] = []
            cloud_music_dict[key].append(item)
            
            # 同时添加只有歌曲名的键，用于模糊匹配
            key_name_only = normalized_name
            if key_name_only not in cloud_music_dict:
                cloud_music_dict[key_name_only] = []
            cloud_music_dict[key_name_only].append(item)
    
    # 过滤VIP歌曲
    for song in vip_songs:
        song_id = song['id']
        song_name = song['name']
        # 获取艺术家名称
        artists = [artist['name'] for artist in song['ar']]
        artists_str = ', '.join(artists)
        
        # 标准化处理
        normalized_name = normalize_song_name(song_name)
        normalized_artists = [normalize_artist_name(artist) for artist in artists]
        
        # 首先检查歌曲ID是否在云盘中（最精确的匹配）
        if song_id in cloud_music_id_dict:
            cloud_item = cloud_music_id_dict[song_id]
            removed_songs.append(song)
            print(f"ID精确匹配: {song_name} - {artists_str} (ID: {song_id})")
            continue
        
        # 检查是否在云盘中 - 精确匹配(歌曲名+艺术家)
        found = False
        for normalized_artist in normalized_artists:
            key = (normalized_name, normalized_artist)
            if key in cloud_music_dict:
                removed_songs.append(song)
                found = True
                print(f"名称精确匹配: {song_name} - {artists_str}")
                break
        
        # 如果精确匹配没找到，尝试只匹配歌曲名
        if not found and normalized_name in cloud_music_dict:
            # 获取云盘中该歌曲名的所有艺术家
            cloud_artists = []
            for item in cloud_music_dict[normalized_name]:
                # 优先使用匹配的艺术家名称
                if item['matched_artist']:
                    cloud_artists.append(normalize_artist_name(item['matched_artist']))
                else:
                    cloud_artists.append(item['normalized_artist'])
            
            # 检查是否有相似的艺术家名称
            for normalized_artist in normalized_artists:
                for cloud_artist in cloud_artists:
                    # 如果艺术家名称包含关系或相似度高，认为是同一首歌
                    if (normalized_artist in cloud_artist or 
                        cloud_artist in normalized_artist or 
                        similarity(normalized_artist, cloud_artist) > 0.7):
                        removed_songs.append(song)
                        found = True
                        cloud_item = cloud_music_dict[normalized_name][0]
                        cloud_name = cloud_item['matched_name'] or cloud_item['name']
                        cloud_artist = cloud_item['matched_artist'] or cloud_item['artist']
                        print(f"模糊匹配: {song_name} - {artists_str} 与云盘中的 {cloud_name} - {cloud_artist}")
                        break
                if found:
                    break
        
        # 如果没有找到匹配，则保留该歌曲
        if not found:
            filtered_songs.append(song)
    
    return filtered_songs, removed_songs


def find_vip_songs(songs, song_urls):
    """从歌曲列表中找出VIP歌曲"""
    vip_songs = []
    
    for song in songs:
        song_id = song['id']
        
        # 只识别会员专享歌曲
        is_vip = False
        vip_type = ""
        
        # 检查歌曲属性，只保留会员专享的判断条件
        if song.get('fee') == 1:
            is_vip = True
            vip_type = "会员专享"
        elif song.get('privilege', {}).get('fee') == 1:
            is_vip = True
            vip_type = "会员专享"
        
        # 检查URL信息，只保留会员专享的判断条件
        if song_id in song_urls:
            url_info = song_urls[song_id]
            if url_info.get('fee') == 1:
                if not is_vip:  # 避免重复添加
                    is_vip = True
                    vip_type = "会员专享"
        
        if is_vip:
            song['vip_type'] = vip_type
            vip_songs.append(song)
    
    return vip_songs


def main():
    """主函数"""
    print("网易云音乐歌单VIP歌曲提取工具")
    print("=" * 30)
    
    # 获取歌单ID
    playlist_id = ""
    saved_playlist_id = get_playlist_id()
    
    if len(sys.argv) > 1:
        playlist_id = sys.argv[1]
        # 保存新提供的歌单ID
        save_playlist_id(playlist_id)
    elif saved_playlist_id:
        # 使用保存的歌单ID
        print(f"使用保存的歌单ID: {saved_playlist_id}")
        playlist_id = saved_playlist_id
    else:
        # 如果没有保存的歌单ID，提示用户输入
        playlist_id = input("请输入歌单ID: ")
        if playlist_id:
            # 保存用户输入的歌单ID
            save_playlist_id(playlist_id)
    
    # 获取Cookie
    cookies = get_cookies()
    
    # 获取歌单中的歌曲ID
    print("正在获取歌单详情...")
    playlist_name, track_ids = get_playlist_detail(playlist_id, cookies)
    print(f"歌单名称: {playlist_name}")
    print(f"共找到 {len(track_ids)} 首歌曲")
    
    if not track_ids:
        print("歌单中没有歌曲")
        return
    
    # 获取歌曲详情
    print("正在获取歌曲详情...")
    songs = get_songs_detail(track_ids, cookies)
    
    # 获取歌曲URL信息，判断VIP歌曲
    print("正在判断VIP歌曲...")
    song_urls = get_song_urls(track_ids, cookies)
    
    # 筛选出VIP歌曲
    vip_songs = find_vip_songs(songs, song_urls)
    
    print(f"找到 {len(vip_songs)} 首VIP歌曲")
    
    # 保存原始VIP歌曲列表
    if vip_songs:
        filename = save_to_markdown(playlist_name, vip_songs)
        print(f"原始结果已保存到 {filename}")
    else:
        print("未找到VIP歌曲")
        return
    
    # 默认过滤云盘中已有的歌曲
    print("正在过滤云盘中已有的歌曲...")
    
    # 获取云盘音乐列表
    cloud_music_info = extract_cloud_music_info(cookies)
    
    # 单独保存云盘音乐列表
    cloud_filename = save_cloud_music_to_markdown(cloud_music_info)
    print(f"云盘音乐列表已保存到 {cloud_filename}")
    
    # 过滤掉云盘中已有的歌曲
    filtered_songs, removed_songs = filter_songs_by_cloud_music(vip_songs, cloud_music_info)
    
    print(f"过滤后剩余 {len(filtered_songs)} 首VIP歌曲")
    print(f"已从列表中移除 {len(removed_songs)} 首云盘中已有的歌曲")
    
    # 保存过滤后的VIP歌曲列表
    if filtered_songs:
        filtered_filename = save_to_markdown(playlist_name, filtered_songs, filtered=True)
        print(f"过滤后的结果已保存到 {filtered_filename}")
    else:
        print("过滤后没有剩余VIP歌曲")


if __name__ == "__main__":
    main() 