import pytest
import requests
import os
import json

API_KEY = os.getenv("API_KEY", "test_key")
BASE_URL = f"http://{os.getenv('TEST_HOST', 'localhost')}:{os.getenv('TEST_PORT', '8000')}"

def test_health_check():
    """测试健康检查接口"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_sql_query():
    """测试SQL查询接口"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "db_name": "prod",
        "sql": "SELECT 1",
        "output_type": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/sql/query",
        headers=headers,
        json=data
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True 