from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional
import os
import time
from database import DatabaseManager
from utils import generate_file_id, save_result_to_file
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 验证 API Key
async def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    scheme, token = authorization.split()
    if scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    if token != os.getenv('API_KEY'):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

@app.post("/sql/query")
async def query_sql(
    request: dict,
    api_key: str = Depends(verify_api_key)
):
    try:
        db_type = request.get("type", "mysql")
        sql = request.get("sql")
        output_type = request.get("output_type", 0)

        if not sql:
            raise HTTPException(status_code=400, detail="SQL query is required")

        db_manager = DatabaseManager()
        result = db_manager.execute_query(db_type, sql)

        if output_type == 0:
            # 生成文件并返回文件ID
            file_id = generate_file_id()
            file_path = save_result_to_file(result, file_id)
            
            return {
                "success": True,
                "result_id": file_id,
                "preview_url": f"/sql/preview/{file_id}.md"
            }
        else:
            # 直接返回查询结果
            return {
                "success": True,
                "result": result
            }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "sql": "ok"
        }
    } 