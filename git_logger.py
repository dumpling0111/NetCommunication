#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file           commit_logger.py
@brief          提取Git最新提交信息并记录到Excel文件的工具
@author         戴飞扬
@date           2025-12-17
@version        1.0
@note           依赖：pandas、openpyxl（Excel写入）、Git环境
@requirements   需要安装依赖：pip install pandas openpyxl
"""

import os
import subprocess
import pandas as pd
from datetime import datetime
import re

# 全局常量：日志Excel文件路径
LOG_FILE = 'commit_log.xlsx'


def get_commit_info():
    """
    @brief      获取Git仓库最新一次提交的核心信息
    @details    执行Git命令提取最新Commit Hash、提交作者、新增代码行数，
                通过正则表达式解析git show --stat的输出结果
    @return     dict    包含提交信息的字典，键说明：
                        - Timestamp: 当前时间戳（格式：YYYY-MM-DD HH:MM:SS）
                        - Commit Hash: 完整的Commit Hash字符串
                        - User: 提交作者名称
                        - Added Lines: 本次提交新增的代码行数（int）
    @exception  subprocess.CalledProcessError  Git命令执行失败（如非Git仓库、命令错误）
    @exception  re.error                      正则表达式解析失败
    @exception  Exception                     其他未知异常（如编码解析失败）
    """
    # 获取最新的Commit Hash（完整哈希值）
    commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()

    # 获取提交作者名称
    author = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%an']).decode().strip()

    # 获取提交的文件变更统计信息
    stats = subprocess.check_output(['git', 'show', '--stat', 'HEAD']).decode().strip()

    # 正则提取新增行数（兼容单复数：insertion/insertions）
    added_lines = 0
    match = re.search(r'(\d+) insertions?\(\+\)', stats)
    if match:
        added_lines = int(match.group(1))

    return {
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Commit Hash': commit_hash,
        'User': author,
        'Added Lines': added_lines
    }


def update_excel(data):
    """
    @brief      将提交信息写入/追加到Excel日志文件
    @details    如果文件已存在则追加新行，不存在则创建新文件；
                写入时自动忽略DataFrame索引，保证Excel格式整洁
    @param      data    dict    由get_commit_info()返回的提交信息字典
    @exception  FileNotFoundError    Excel文件路径不存在（权限/路径错误）
    @exception  PermissionError      无Excel文件写入权限
    @exception  Exception             pandas写入Excel时的其他异常（如格式错误）
    @note       依赖openpyxl库处理.xlsx格式，需提前安装
    """
    if os.path.exists(LOG_FILE):
        # 读取已有文件并追加新数据
        df = pd.read_excel(LOG_FILE)
        new_df = pd.DataFrame([data])
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        # 创建新的DataFrame
        df = pd.DataFrame([data])

    # 写入Excel文件（忽略索引）
    df.to_excel(LOG_FILE, index=False)
    print(f"Commit log updated: {data}")


if __name__ == '__main__':
    """
    @brief      程序主入口
    @details    调用提交信息提取和Excel写入函数，捕获所有异常并打印错误信息
    """
    try:
        commit_info = get_commit_info()
        update_excel(commit_info)
    except Exception as e:
        print(f"Error logging commit: {e}")
