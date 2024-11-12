import os
import time
import uuid
from typing import List, Tuple

def format_result(columns: List[str], rows: List[Tuple]) -> str:
    """格式化查询结果为Markdown表格
    
    Args:
        columns: 列名列表
        rows: 数据行列表
        
    Returns:
        markdown格式的表格字符串
    """
    if not columns:
        return "No results"
        
    # 构建表头
    result = "| " + " | ".join(str(col) for col in columns) + " |\n"
    result += "|" + "|".join(["---" for _ in columns]) + "|\n"
    
    # 添加数据行，确保所有值都正确编码
    for row in rows:
        formatted_row = []
        for cell in row:
            if isinstance(cell, bytes):
                cell = cell.decode('utf-8')
            formatted_row.append(str(cell))
        result += "| " + " | ".join(formatted_row) + " |\n"
        
    return result

def save_result_to_file(content: str) -> str:
    """保存查询结果到文件
    
    Args:
        content: 要保存的内容
        
    Returns:
        文件ID
    """
    # 生成唯一文件ID
    file_id = str(int(time.time() * 1000))
    
    # 确保目录存在
    os.makedirs("data/sql", exist_ok=True)
    
    # 保存文件，使用 utf-8 编码
    file_path = f"data/sql/{file_id}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return file_id

def clean_expired_files(expiry_hours: int = 48):
    """清理过期文件
    
    Args:
        expiry_hours: 文件过期时间(小时)
    """
    try:
        current_time = time.time()
        sql_dir = "data/sql"
        
        if not os.path.exists(sql_dir):
            return
            
        for filename in os.listdir(sql_dir):
            file_path = os.path.join(sql_dir, filename)
            file_modified_time = os.path.getmtime(file_path)
            
            if current_time - file_modified_time > expiry_hours * 3600:
                os.remove(file_path)
                
    except Exception as e:
        print(f"Error cleaning expired files: {e}")