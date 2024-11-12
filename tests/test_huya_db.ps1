# 测试配置
$API_KEY = "ZogFaJFxiEBW142g3g"
$BASE_URL = "http://localhost:8090"

# 请求头
$headers = @{
    "Authorization" = "Bearer $API_KEY"
    "Content-Type" = "application/json"
}

# 请求体
$body = @{
    "db_name" = "huya"
    "sql" = "select * from huyadata.cal_icr_ayyuid limit 5"
    "output_type" = 1
} | ConvertTo-Json

try {
    Write-Host "正在发送查询请求..." -ForegroundColor Yellow
    
    # 设置响应编码
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    
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