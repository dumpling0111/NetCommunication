import os
import subprocess
import pandas as pd
from datetime import datetime
import re

LOG_FILE = 'commit_log.xlsx'

def get_commit_info():
    # 获取最新的 Commit Hash
    commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    # 获取作者
    author = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%an']).decode().strip()
    # 获取新增/修改统计信息
    # git show --stat 包含类似 " 1 file changed, 2 insertions(+)"
    stats = subprocess.check_output(['git', 'show', '--stat', 'HEAD']).decode().strip()

    # 使用正则提取新增行数 (insertions)
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
    if os.path.exists(LOG_FILE):
        df = pd.read_excel(LOG_FILE)
        new_df = pd.DataFrame([data])
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(LOG_FILE, index=False)
    print(f"Commit log updated: {data}")

if __name__ == '__main__':
    try:
        info = get_commit_info()
        update_excel(info)
    except Exception as e:
        print(f"Error logging commit: {e}")
