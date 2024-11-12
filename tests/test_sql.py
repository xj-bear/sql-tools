import unittest
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class TestSQLAPI(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.base_url = "http://localhost:6"
        self.api_key = os.getenv('API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def test_health_check(self):
        """测试健康检查接口"""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['services']['sql'], 'ok')

    def test_mysql_query(self):
        """测试MySQL查询"""
        payload = {
            "type": "mysql",
            "sql": "SELECT 1 as test",
            "output_type": 1  # 直接返回结果
        }
        response = requests.post(
            f"{self.base_url}/sql/query",
            headers=self.headers,
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('| test |', data['result'])
        self.assertIn('| 1 |', data['result'])

    def test_mysql_query_with_file(self):
        """测试MySQL查询并生成文件"""
        payload = {
            "type": "mysql",
            "sql": "SELECT 1 as test",
            "output_type": 0  # 生成文件
        }
        response = requests.post(
            f"{self.base_url}/sql/query",
            headers=self.headers,
            json=payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue('result_id' in data)
        self.assertTrue('preview_url' in data)

        # 测试预览URL
        preview_response = requests.get(f"{self.base_url}{data['preview_url']}")
        self.assertEqual(preview_response.status_code, 200)
        self.assertIn('| test |', preview_response.text)
        self.assertIn('| 1 |', preview_response.text)

    def test_invalid_sql(self):
        """测试无效的SQL语句"""
        payload = {
            "type": "mysql",
            "sql": "INVALID SQL",
            "output_type": 1
        }
        response = requests.post(
            f"{self.base_url}/sql/query",
            headers=self.headers,
            json=payload
        )
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertTrue('error' in data)

    def test_missing_auth(self):
        """测试缺少认证"""
        payload = {
            "type": "mysql",
            "sql": "SELECT 1",
            "output_type": 1
        }
        response = requests.post(
            f"{self.base_url}/sql/query",
            json=payload
        )
        self.assertEqual(response.status_code, 401)

    def test_invalid_auth(self):
        """测试无效的认证"""
        headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        payload = {
            "type": "mysql",
            "sql": "SELECT 1",
            "output_type": 1
        }
        response = requests.post(
            f"{self.base_url}/sql/query",
            headers=headers,
            json=payload
        )
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main() 