# 寻声觅迹后端

这是“寻声觅迹 ECHO TRAIL”黑客松MVP的后端服务。目前已完成匿名身份、歌曲、歌词、省份、播放记录、三类票根核心闭环和云端部署适配。

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

## 5. 当前接口

- `POST /api/v1/sessions/anonymous`
- `GET /api/v1/users/me`
- `GET /api/v1/songs`
- `GET /api/v1/songs/{song_id}`
- `GET /api/v1/songs/{song_id}/lyrics`
- `GET /api/v1/provinces`
- `GET /api/v1/provinces/{province_code}`
- `GET /api/v1/provinces/{province_code}/song-recommendations`
- `GET /api/v1/provinces/{province_code}/emotion-map`
- `GET /api/v1/resonance?song_id={song_id}&province_code={province_code}`
- `POST /api/v1/uploads/ticket-photo`
- `POST /api/v1/play-events`
- `POST /api/v1/tickets`
- `GET /api/v1/tickets`
- `GET /api/v1/tickets/{ticket_id}`
- `GET /api/v1/health`

受保护接口需在请求头中携带：

```text
Authorization: Bearer <access_token>
```

## 6. 票根调用顺序

1. 调用`POST /sessions/anonymous`取得访问令牌。
2. 携带令牌调用`GET /songs`取得歌曲编号。
3. 调用`GET /songs/{song_id}/lyrics`取得可选歌词编号。
4. 用户点击播放时调用`POST /play-events`取得播放记录编号。
5. 调用`POST /tickets`并提交歌曲、播放记录、省份、票种和编辑内容。
6. 调用`GET /tickets`查看个人票根列表。
7. 调用`GET /provinces`查看个人地图点亮状态。

## 7. 第三阶段业务规则

- 播放记录24小时内有效，且必须属于当前匿名用户和当前歌曲。
- 广东、陕西可创建票根，其他省份只提供占位信息。
- 烫银票必须提供照片地址；烫金和原纸票不能提供照片地址。
- 一张票根最多选择三个固定心情标签。
- `idempotency_key`用于防止用户重复点击生成两张相同票根。
- 票根保存歌名、歌手、封面和歌词快照，避免原始歌曲变化影响历史票根。
- 本阶段只接收已有照片地址，真实图片上传在第五阶段实现。

## 8. 地图与共鸣统计

- 共鸣人数按照匿名用户去重，同一用户制作多张相同歌曲票根只计一位。
- 展示人数由演示基数加真实新增用户数构成，并返回`is_demo_data`标记。
- 广东和陕西各返回本周最多点亮、今日地区主题曲、雨天、深夜和旅行者首选五类内容。
- 本周同一歌曲真实票根达到三张时，可以替换预置的“本周最多点亮”。
- 心情分布由演示基数叠加真实票根心情，并保证百分比合计为100%。
- 创建票根的响应会直接包含最新共鸣人数。
- 所有群体接口只返回汇总数量，不返回其他用户身份、地点、照片或票根内容。

## 9. 图片上传

- 支持JPEG、PNG和WebP，原始文件最大5MB、最大2000万像素。
- 图片自动纠正方向，最长边缩小到2048像素，并统一转换为WebP。
- 重新编码会移除EXIF及GPS元数据。
- 文件名由后端随机生成，上传目录不会提交到Git。
- 烫银票只接受本服务上传并且仍然存在的图片地址。
- 本地开发默认使用本地图片目录，线上通过环境变量切换为腾讯云COS。

## 10. 第六阶段部署适配

- 根目录`render.yaml`定义Render Web Service和PostgreSQL。
- `start.sh`会在启动时执行数据库迁移和演示数据初始化。
- `DATABASE_URL`可以使用Render提供的PostgreSQL连接地址。
- `STORAGE_BACKEND=local`使用本地图片，`STORAGE_BACKEND=cos`使用腾讯云COS。
- COS密钥只通过Render环境变量提供，不写入Git。
- 完整的零基础操作步骤见[docs/render-deployment.md](docs/render-deployment.md)。

前端未来接入时参考：[docs/frontend-integration.md](docs/frontend-integration.md)。
