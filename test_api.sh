#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
API_URL="http://localhost:6"
API_KEY="ZogFaJFxiEBW142g3g"

# 辅助函数
print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

check_response() {
    if [ $1 -eq $2 ]; then
        echo -e "${GREEN}✓ 测试通过: 状态码 $1${NC}"
    else
        echo -e "${RED}✗ 测试失败: 期望状态码 $2, 实际状态码 $1${NC}"
        return 1
    fi
}

# 1. 测试健康检查接口
test_health_check() {
    print_header "测试健康检查接口"
    
    response=$(curl -s -w "\n%{http_code}" $API_URL/health)
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    check_response $status_code 200
}

# 2. 测试MySQL查询 - 直接返回结果
test_mysql_query() {
    print_header "测试MySQL查询 - 直接返回结果"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "mysql",
            "sql": "SELECT 1 as test",
            "output_type": 1
        }' \
        $API_URL/sql/query)
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    check_response $status_code 200
    
    # 检查返回的JSON
    if echo "$body" | grep -q '"success":true'; then
        echo -e "${GREEN}✓ 测试通过: 返回成功标志${NC}"
    else
        echo -e "${RED}✗ 测试失败: 未返回成功标志${NC}"
        return 1
    fi
}

# 3. 测试MySQL查询 - 生成文件
test_mysql_query_file() {
    print_header "测试MySQL查询 - 生成文件"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "mysql",
            "sql": "SELECT 1 as test",
            "output_type": 0
        }' \
        $API_URL/sql/query)
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    check_response $status_code 200
    
    # 获取预览URL
    preview_url=$(echo $body | grep -o '"preview_url":"[^"]*"' | cut -d'"' -f4)
    
    if [ ! -z "$preview_url" ]; then
        echo -e "${GREEN}✓ 测试通过: 成功获取预览URL${NC}"
        
        # 测试预览URL访问
        preview_response=$(curl -s -w "\n%{http_code}" $API_URL$preview_url)
        preview_status_code=$(echo "$preview_response" | tail -n1)
        preview_body=$(echo "$preview_response" | sed '$d')
        
        check_response $preview_status_code 200
    else
        echo -e "${RED}✗ 测试失败: 未获取到预览URL${NC}"
        return 1
    fi
}

# 4. 测试无效SQL
test_invalid_sql() {
    print_header "测试无效SQL"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "mysql",
            "sql": "INVALID SQL",
            "output_type": 1
        }' \
        $API_URL/sql/query)
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    check_response $status_code 500
}

# 5. 测试无效认证
test_invalid_auth() {
    print_header "测试无效认证"
    
    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer invalid_token" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "mysql",
            "sql": "SELECT 1",
            "output_type": 1
        }' \
        $API_URL/sql/query)
    
    status_code=$(echo "$response" | tail -n1)
    check_response $status_code 401
}

# 运行所有测试
run_all_tests() {
    echo -e "${YELLOW}开始运行API测试...${NC}"
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 5
    
    # 运行测试
    test_health_check
    test_mysql_query
    test_mysql_query_file
    test_invalid_sql
    test_invalid_auth
    
    echo -e "\n${YELLOW}测试完成${NC}"
}

# 执行测试
run_all_tests 