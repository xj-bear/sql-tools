from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional
import os
import json
from database import DatabaseManager
from utils import format_result, save_result_to_file
from pydantic import BaseModel

app = FastAPI()

# 从环境变量获取数据库配置
database_configs = os.getenv("DATABASE_CONFIGS", "{}")
db_manager = DatabaseManager(database_configs)

class QueryRequest(BaseModel):
    db_name: str
    sql: str
    output_type: int = 0  # 0: 生成文件, 1: 直接返回结果

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
        
        if request.output_type == 0:
            # 生成文件并返回文件ID
            result_str = format_result(columns, rows)
            file_id = save_result_to_file(result_str)
            return {
                "success": True,
                "result_id": file_id,
                "preview_url": f"/sql/preview/{file_id}.md"
            }
        else:
            # 直接返回查询结果
            return {
                "success": True,
                "result": format_result(columns, rows)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    db_manager.close_all()