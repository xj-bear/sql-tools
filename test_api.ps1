# 颜色定义
$RED = 'Red'
$GREEN = 'Green'
$YELLOW = 'Yellow'

# 配置
$API_URL = "http://localhost:6"
$API_KEY = "ZogFaJFxiEBW142g3g"

# 辅助函数
function Write-Header {
    param($text)
    Write-Host "`n=== $text ===`n" -ForegroundColor $YELLOW
}

function Test-Response {
    param($actual, $expected)
    if ($actual -eq $expected) {
        Write-Host "✓ 测试通过: 状态码 $actual" -ForegroundColor $GREEN
        return $true
    } else {
        Write-Host "✗ 测试失败: 期望状态码 $expected, 实际状态码 $actual" -ForegroundColor $RED
        return $false
    }
}

# 1. 测试健康检查接口
function Test-HealthCheck {
    Write-Header "测试健康检查接口"
    
    try {
        $response = Invoke-RestMethod -Uri "$API_URL/health" -Method Get -StatusCodeVariable statusCode
        return Test-Response $statusCode 200
    } catch {
        Write-Host "✗ 测试失败: $_" -ForegroundColor $RED
        return $false
    }
}

# 2. 测试MySQL查询 - 直接返回结果
function Test-MySQLQuery {
    Write-Header "测试MySQL查询 - 直接返回结果"
    
    try {
        $body = @{
            type = "mysql"
            sql = "SELECT 1 as test"
            output_type = 1
        } | ConvertTo-Json

        $headers = @{
            "Authorization" = "Bearer $API_KEY"
            "Content-Type" = "application/json"
        }

        $response = Invoke-RestMethod -Uri "$API_URL/sql/query" -Method Post -Body $body -Headers $headers -StatusCodeVariable statusCode
        
        if (-not (Test-Response $statusCode 200)) { return $false }
        
        if ($response.success) {
            Write-Host "✓ 测试通过: 返回成功标志" -ForegroundColor $GREEN
            return $true
        } else {
            Write-Host "✗ 测试失败: 未返回成功标志" -ForegroundColor $RED
            return $false
        }
    } catch {
        Write-Host "✗ 测试失败: $_" -ForegroundColor $RED
        return $false
    }
}

# 运行所有测试
function Run-AllTests {
    Write-Host "开始运行API测试..." -ForegroundColor $YELLOW
    
    # 等待服务启动
    Write-Host "等待服务启动..."
    Start-Sleep -Seconds 5
    
    # 运行测试
    Test-HealthCheck
    Test-MySQLQuery
    
    Write-Host "`n测试完成" -ForegroundColor $YELLOW
}

# 执行测试
Run-AllTests