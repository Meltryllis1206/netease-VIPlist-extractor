#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import base64
from Crypto.Cipher import AES
from binascii import hexlify

# AES加密相关参数
MODULUS = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
NONCE = '0CoJUm6Qyw8W8jud'
PUBKEY = '010001'
IV = '0102030405060708'


def create_secret_key(size):
    """生成指定长度的随机字符串作为密钥"""
    return hexlify(os.urandom(size))[:16].decode('utf-8')


def aes_encrypt(text, key):
    """AES加密"""
    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad
    encryptor = AES.new(key.encode(), AES.MODE_CBC, IV.encode())
    encrypt_text = encryptor.encrypt(text.encode())
    encrypt_text = base64.b64encode(encrypt_text).decode('utf-8')
    return encrypt_text


def rsa_encrypt(text, pubkey, modulus):
    """RSA加密"""
    text = text[::-1]
    rs = pow(int(hexlify(text.encode('utf-8')), 16), int(pubkey, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)


def encrypted_request(text):
    """加密请求数据"""
    text = json.dumps(text)
    sec_key = create_secret_key(16)
    enc_text = aes_encrypt(aes_encrypt(text, NONCE), sec_key)
    enc_sec_key = rsa_encrypt(sec_key, PUBKEY, MODULUS)
    return {
        'params': enc_text,
        'encSecKey': enc_sec_key
    } 