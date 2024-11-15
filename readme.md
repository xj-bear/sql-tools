# SQL Plugin Service v0.2

这是一个支持多数据库查询的Docker服务，可以独立运行或集成到Dify中使用。

## 功能特点
- 支持多数据库配置(MySQL/MariaDB、Presto、Hive)
- 支持通过数据库别名切换不同数据库
- 提供SQL查询和结果导出功能
- 支持多种输出格式：
  - Markdown表格（file_md, out_md）
  - CSV文件（file_csv）
  - JSON格式（out_json）
- UTF-8编码支持
- Bearer Token认证
- 自动重连和连接池管理
- 健康检查和错误重试

## 版本更新
### v0.2
- 新增多种输出格式支持（CSV、JSON）
- 优化输出类型命名规范
- 改进日期时间类型处理
- 增强中文编码支持
- 添加数据库连接池管理
- 实现自动重连机制

### v0.1
- 初始版本发布
- 支持基础SQL查询功能
- Markdown格式输出支持

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/xj-bear/sql-tools.git
cd sql-tools
```

### 2. 配置环境
```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件，填入实际配置
vim .env
```

### 3. 构建和启动
```bash
# 方式1：使用预构建镜像
docker-compose pull
docker-compose up -d

# 方式2：本地构建
docker-compose build --no-cache
docker-compose up -d
```

## 配置说明

### 1. 环境配置
在 `.env` 文件中配置:
```bash
# API密钥
API_KEY=your_api_key

# 数据库配置(JSON格式)
DATABASE_CONFIGS='{"prod":{"type":"mysql","host":"host1","port":3306,"user":"user1","password":"pass1"}}'

# 其他配置
FILE_EXPIRY_HOURS=48  # 文件过期时间
WORKERS=4             # 工作进程数
THREADS=2            # 线程数
TIMEOUT=120          # 超时时间(秒)
```

## API使用说明

### 1. 外部直接调用
从外部系统访问服务时使用 `http://localhost:8090`

```bash
# curl示例 - JSON输出
curl -X POST http://localhost:8090/sql/query \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "db_name": "prod",
         "sql": "SELECT * FROM table LIMIT 5",
         "output_type": "out_json"
     }'

# PowerShell示例 - CSV文件输出
$headers = @{
    "Authorization" = "Bearer $API_KEY"
    "Content-Type" = "application/json"
}

$body = @{
    "db_name" = "prod"
    "sql" = "SELECT * FROM table LIMIT 5"
    "output_type" = "file_csv"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Method Post `
    -Uri "$BASE_URL/sql/query" `
    -Headers $headers `
    -Body $body
```

### 2. Dify内部调用
在Dify容器网络内部访问服务时使用 `http://plugin-services:8000`

```python
# Dify插件示例
import requests

def query_sql(db_name: str, sql: str, output_type: str = "out_json"):
    response = requests.post(
        "http://plugin-services:8000/sql/query",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "db_name": db_name,
            "sql": sql,
            "output_type": output_type
        }
    )
    return response.json()
```

## 部署说明

### 1. 独立部署
```bash
# 克隆项目
git clone https://github.com/xj-bear/sql-tools.git
cd sql-tools

# 配置环境
cp .env.example .env
vim .env  # 编辑配置文件

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. 集成到Dify
1. 确保SQL服务和Dify在同一网络中
2. 在dify-yaml.yaml中添加环境变量：
```yaml
services:
  api:
    environment:
      SQL_SERVICE_URL: http://plugin-services:8000
```

## 网络说明
- 外部访问: `http://localhost:8090`
- Dify内部访问: `http://plugin-services:8000`

## 故障排查
1. 检查服务状态
```bash
docker ps
docker-compose ps
```

2. 检查服务健康
```bash
curl http://localhost:8090/health
```

3. 查看日志
```bash
docker-compose logs -f plugin-services
```

4. 常见问题
- 认证失败：检查API_KEY配置
- 数据库连接失败：检查DATABASE_CONFIGS配置
- 中文乱码：确认数据库和程序使用UTF-8编码
- JSON序列化错误：检查数据类型兼容性
- 连接断开：服务会自动重连，如果持续失败请检查数据库状态

## 安全建议
1. 修改默认API_KEY
2. 限制数据库用户权限
3. 使用网络隔离
4. 定期更新依赖包
5. 注意敏感数据处理