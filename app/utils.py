import os
import time
import json
from datetime import date, datetime
from typing import List, Tuple
from io import StringIO
import csv

class DateTimeEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理日期时间类型"""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def format_result(columns: List[str], rows: List[Tuple], output_type: str) -> str:
    """格式化查询结果
    
    Args:
        columns: 列名列表
        rows: 数据行列表
        output_type: 输出类型(file_md/file_csv/out_md/out_json)
        
    Returns:
        格式化后的字符串
    """
    if not columns:
        return "No results"
        
    if output_type in ['file_md', 'out_md']:
        # Markdown格式
        result = "| " + " | ".join(str(col) for col in columns) + " |\n"
        result += "|" + "|".join(["---" for _ in columns]) + "|\n"
        
        for row in rows:
            formatted_row = []
            for cell in row:
                if isinstance(cell, bytes):
                    cell = cell.decode('utf-8')
                elif isinstance(cell, (date, datetime)):
                    cell = cell.isoformat()
                formatted_row.append(str(cell))
            result += "| " + " | ".join(formatted_row) + " |\n"
            
        return result
        
    elif output_type in ['file_csv', 'out_csv']:
        # CSV格式
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        for row in rows:
            formatted_row = []
            for cell in row:
                if isinstance(cell, bytes):
                    cell = cell.decode('utf-8')
                elif isinstance(cell, (date, datetime)):
                    cell = cell.isoformat()
                formatted_row.append(str(cell))
            writer.writerow(formatted_row)
        return output.getvalue()
        
    elif output_type == 'out_json':
        try:
            # JSON格式
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, bytes):
                        value = value.decode('utf-8')
                    elif isinstance(value, (date, datetime)):
                        value = value.isoformat()
                    elif value is None:
                        value = None
                    else:
                        value = str(value)
                    row_dict[col] = value
                result.append(row_dict)
            
            # 使用自定义编码器进行JSON序列化
            json_str = json.dumps(result, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            print(f"JSON result: {json_str}")  # 添加调试日志
            return json_str
            
        except Exception as e:
            print(f"Error formatting JSON: {str(e)}")  # 添加调试日志
            raise
        
    else:
        raise ValueError(f"Unsupported output type: {output_type}")

def save_result_to_file(content: str, output_type: str) -> str:
    """保存查询结果到文件
    
    Args:
        content: 要保存的内容
        output_type: 输出类型(file_md/file_csv)
        
    Returns:
        文件ID
    """
    # 生成唯一文件ID
    file_id = str(int(time.time() * 1000))
    
    # 确保目录存在
    os.makedirs("data/sql", exist_ok=True)
    
    # 根据输出类型确定文件扩展名
    ext = '.md' if output_type == 'file_md' else '.csv'
    
    # 保存文件
    file_path = f"data/sql/{file_id}{ext}"
    with open(file_path, "w", encoding="utf-8", newline='') as f:
        f.write(content)
        
    return file_id

def get_preview_url(file_id: str, output_type: str) -> str:
    """获取预览URL
    
    Args:
        file_id: 文件ID
        output_type: 输出类型
        
    Returns:
        预览URL
    """
    ext = '.md' if output_type == 'file_md' else '.csv'
    return f"/sql/preview/{file_id}{ext}"

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