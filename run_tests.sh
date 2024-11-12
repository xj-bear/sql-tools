#!/bin/bash

# 等待服务启动
echo "Waiting for services to start..."
sleep 5

# 运行测试
python -m pytest tests/ -v 