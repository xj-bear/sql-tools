from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional
import os
from enum import Enum
from database import DatabaseManager
from utils import format_result, save_result_to_file, get_preview_url
from pydantic import BaseModel

app = FastAPI()

# 从环境变量获取数据库配置
database_configs = os.getenv("DATABASE_CONFIGS", "{}")
db_manager = DatabaseManager(database_configs)

class OutputType(str, Enum):
    file_md = "file_md"
    file_csv = "file_csv"
    out_md = "out_md"
    out_json = "out_json"

class QueryRequest(BaseModel):
    db_name: str
    sql: str
    output_type: OutputType = OutputType.out_md

async def verify_token(authorization: str = Header(...)):
    """验证API Token"""
    api_key = os.getenv("API_KEY")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    if token != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token

@app.post("/sql/query")
async def query_sql(request: QueryRequest, token: str = Depends(verify_token)):
    """执行SQL查询
    
    Args:
        request: 包含db_name、sql和output_type的请求体
        token: API认证token
    
    Returns:
        查询结果或文件ID
    """
    try:
        columns, rows = db_manager.execute_query(request.db_name, request.sql)
        
        # 格式化结果
        result_str = format_result(columns, rows, request.output_type)
        
        if request.output_type.startswith('file_'):
            # 生成文件并返回文件ID
            file_id = save_result_to_file(result_str, request.output_type)
            return {
                "success": True,
                "result_id": file_id,
                "preview_url": get_preview_url(file_id, request.output_type)
            }
        else:
            # 直接返回查询结果
            return {
                "success": True,
                "result": result_str,
                "result_type": request.output_type
            }
            
    except Exception as e:
        print(f"Error in query_sql: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    db_manager.close_all()