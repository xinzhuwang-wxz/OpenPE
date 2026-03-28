# VikingDB FastAPI Server

重构后的 VikingDB Collection Server，使用 FastAPI 替代 Flask。

## 文件说明

- **app_models.py**: Pydantic 数据模型定义 (替代 Flask-RESTful 的 reqparse)
- **api_fastapi.py**: FastAPI 路由和 API 端点 (替代 Flask-RESTful 的 Resource 类)
- **server_fastapi.py**: FastAPI 主服务器文件 (替代 Flask 应用)

## 安装依赖

```bash
pip install fastapi uvicorn pydantic
```

## 运行服务

### 方式 1: 直接运行
```bash
cd openviking/storage/vectordb/service
python server_fastapi.py
```

### 方式 2: 使用 uvicorn 运行
```bash
cd openviking/storage/vectordb/service
uvicorn server_fastapi:app --host 0.0.0.0 --port 5000 --reload
```

## 配置

### 环境变量
- `VIKINGDB_PERSIST_PATH`: 数据持久化路径，默认为 `./vikingdb_data/`
  - 设置为空字符串使用 volatile mode (内存模式)
  - 设置为路径使用 persistent mode (持久化模式)

示例:
```bash
export VIKINGDB_PERSIST_PATH="./my_data_path/"
python server_fastapi.py
```

## API 文档

FastAPI 自动生成交互式 API 文档:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## API 端点

### Collection APIs
- `POST /CreateVikingdbCollection` - 创建 Collection
- `POST /UpdateVikingdbCollection` - 更新 Collection
- `GET /GetVikingdbCollection` - 获取 Collection 信息
- `GET /ListVikingdbCollection` - 列出所有 Collections
- `POST /DeleteVikingdbCollection` - 删除 Collection

### Data APIs
- `POST /api/vikingdb/data/upsert` - 写入/更新数据
- `GET /api/vikingdb/data/fetch_in_collection` - 获取数据
- `POST /api/vikingdb/data/delete` - 删除数据

### Index APIs
- `POST /CreateVikingdbIndex` - 创建索引
- `POST /UpdateVikingdbIndex` - 更新索引
- `GET /GetVikingdbIndex` - 获取索引信息
- `GET /ListVikingdbIndex` - 列出所有索引
- `POST /DeleteVikingdbIndex` - 删除索引

### Search APIs
- `POST /api/vikingdb/data/search/vector` - 向量搜索
- `POST /api/vikingdb/data/search/id` - 通过 ID 搜索
- `POST /api/vikingdb/data/search/multi_modal` - 多模态搜索
- `POST /api/vikingdb/data/search/scalar` - 标量字段搜索
- `POST /api/vikingdb/data/search/random` - 随机搜索
- `POST /api/vikingdb/data/search/keywords` - 关键词搜索

### 健康检查
- `GET /` - 根端点
- `GET /health` - 健康检查端点

## 主要改进

### 1. 现代化框架
- 使用 FastAPI 替代 Flask，性能更好
- 支持异步操作
- 自动生成 OpenAPI 文档

### 2. 类型安全
- 使用 Pydantic 模型进行请求验证
- 自动类型检查和数据验证
- 更好的 IDE 支持

### 3. 更好的开发体验
- 自动交互式 API 文档 (Swagger UI)
- 请求和响应的自动验证
- 更清晰的错误消息

### 4. 性能提升
- FastAPI 基于 Starlette 和 Pydantic，性能优于 Flask
- 支持异步处理
- 更高效的请求处理

## 与原 Flask 版本的兼容性

API 端点路径和请求/响应格式与原 Flask 版本完全兼容，可以无缝切换。

## 测试

使用 curl 测试:

```bash
# 创建 Collection
curl -X POST "http://localhost:5000/CreateVikingdbCollection" \
  -H "Content-Type: application/json" \
  -d '{
    "CollectionName": "test_collection",
    "ProjectName": "default",
    "Description": "Test collection",
    "Fields": "[{\"FieldName\":\"id\",\"FieldType\":\"int64\",\"IsPrimaryKey\":true},{\"FieldName\":\"text\",\"FieldType\":\"string\"}]"
  }'

# 获取健康状态
curl "http://localhost:5000/health"
```

使用 Python requests:

```python
import requests
import json

# 创建 Collection
response = requests.post(
    "http://localhost:5000/CreateVikingdbCollection",
    json={
        "CollectionName": "test_collection",
        "ProjectName": "default",
        "Description": "Test collection",
        "Fields": json.dumps([
            {
                "FieldName": "id",
                "FieldType": "int64",
                "IsPrimaryKey": True
            },
            {
                "FieldName": "text",
                "FieldType": "string"
            }
        ])
    }
)
print(response.json())
```
