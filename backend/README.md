# 寻声觅迹后端

这是“寻声觅迹 ECHO TRAIL”黑客松MVP的后端服务。第二阶段包含匿名身份、歌曲、歌词、省份、SQLite数据库和基础测试，暂不包含票根生成。

## 1. 环境要求

- 推荐Python 3.12
- 当前代码兼容Python 3.9及以上版本

## 2. 第一次运行

进入后端目录：

```bash
cd backend
```

创建虚拟环境：

```bash
python3 -m venv .venv
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

复制本地配置：

```bash
cp .env.example .env
```

创建数据库结构：

```bash
alembic upgrade head
```

写入广东、陕西及其他省份演示数据：

```bash
python -m app.seed.run
```

启动服务：

```bash
uvicorn app.main:app --reload
```

打开以下地址：

- 接口文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health

## 3. 自动测试

```bash
python -m pytest -q
```

## 4. 初学者需要知道的文件

- `app/main.py`：后端服务入口。
- `app/api/v1/routes/`：前端可以请求的接口。
- `app/models/`：数据库表结构。
- `app/schemas/`：接口数据格式。
- `app/repositories/`：数据库读取与写入。
- `app/services/`：业务规则。
- `app/seed/`：演示数据初始化。
- `migrations/`：数据库结构变更历史。
- `tests/`：自动测试。

## 5. 第二阶段接口

- `POST /api/v1/sessions/anonymous`
- `GET /api/v1/users/me`
- `GET /api/v1/songs`
- `GET /api/v1/songs/{song_id}`
- `GET /api/v1/songs/{song_id}/lyrics`
- `GET /api/v1/provinces`
- `GET /api/v1/provinces/{province_code}`
- `GET /api/v1/health`

受保护接口需在请求头中携带：

```text
Authorization: Bearer <access_token>
```
