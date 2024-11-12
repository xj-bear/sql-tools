# SQL Plugin Service

这是一个支持多数据库查询的Docker服务。

## 功能特点
- 支持多数据库配置(MySQL/MariaDB、Presto、Hive)
- 支持通过数据库别名切换不同数据库
- 提供SQL查询和结果导出功能
- 支持结果格式化为Markdown表格

## 配置说明

### 1. 环境配置
在 `.env` 文件中配置:
```bash
# API密钥
API_KEY=your_api_key

# 数据库配置(JSON格式)
DATABASE_CONFIGS={"db_alias":{"type":"mysql","host":"host","port":3306,"user":"user","password":"pass"}}
```

### 2. API使用
```bash
# SQL查询
curl -X POST http://plugin-services:8000/sql/query \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
         "db_name": "prod",
         "sql": "SELECT * FROM table LIMIT 5",
         "output_type": 0
     }'
```

## 部署说明
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```



$API_KEY = "ZogFaJFxiEBW142g3g"
$BASE_URL = "http://localhost:8090"

$headers = @{
    "Authorization" = "Bearer $API_KEY"
    "Content-Type" = "application/json"
}

$body = @{
    "db_name" = "huya"
    "sql" = "select * from huyadata.cal_icr_ayyuid limit 5"
    "output_type" = 0
} | ConvertTo-Json

try {
    Write-Host "正在发送查询请求..."
    
    $response = Invoke-RestMethod `
        -Method Post `
        -Uri "$BASE_URL/sql/query" `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json"
    
    if ($response.success) {
        Write-Host "查询成功！" -ForegroundColor Green
        Write-Host "查询结果："
        Write-Host $response.result
    } else {
        Write-Host "查询失败！" -ForegroundColor Red
        Write-Host $response.error
    }
} catch {
    Write-Host "发生错误：" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host "响应内容："
    Write-Host $_.ErrorDetails.Message
}