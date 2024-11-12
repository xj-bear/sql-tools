import os
import time
import random

def generate_file_id():
    """生成唯一的文件ID"""
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    return f"{timestamp}{random_num}"

def save_result_to_file(content: str, file_id: str) -> str:
    """保存查询结果到文件"""
    os.makedirs("data/sql", exist_ok=True)
    file_path = f"data/sql/{file_id}.md"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return file_path 