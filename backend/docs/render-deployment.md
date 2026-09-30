# Render与腾讯云COS部署指南

本项目的线上架构是：Render Web Service运行FastAPI，Render PostgreSQL保存用户、播放和票根数据，腾讯云COS保存票根照片。不需要Render磁盘和自定义域名。

## 1. 部署前准备

1. GitHub仓库已包含根目录的`render.yaml`。
2. 在腾讯云COS创建一个存储桶，选择靠近主要演示用户的地域。
3. 记录存储桶全称、地域代码和访问域名。
4. 创建仅能访问该存储桶的CAM子用户，不使用主账号密钥。
5. 保存SecretId和SecretKey，不要把它们写入代码、文档或Git。

MVP如果需要直接展示图片，可以使用公有读存储桶。请确保只上传用户明确选择的演示照片；正式产品应改为私有读和临时签名URL。

## 2. Render环境变量

Render会根据`render.yaml`自动配置`APP_ENV`、`DATABASE_URL`、`STORAGE_BACKEND`和`CORS_ORIGINS`。创建Blueprint时需手动填写：

- `COS_SECRET_ID`：CAM子用户SecretId。
- `COS_SECRET_KEY`：CAM子用户SecretKey。
- `COS_REGION`：例如`ap-guangzhou`。
- `COS_BUCKET`：包含APPID的完整桶名，例如`echo-trail-1250000000`。
- `COS_PUBLIC_BASE_URL`：不带末尾斜杠的COS访问地址。

如果后续前端地址发生变化，需在Render中更新`CORS_ORIGINS`，多个地址使用英文逗号分隔。

## 3. 创建Render Blueprint

1. 登录Render，选择New > Blueprint。
2. 连接GitHub仓库`wenhuaruyu/echo-trail`。
3. Render读取`render.yaml`后，确认Web Service和PostgreSQL各一个。
4. 填写上述五个COS秘密环境变量后创建。
5. 部署时`start.sh`会先升级数据库结构、写入演示数据，再启动接口。

## 4. 上线验收

假设Render分配的地址是`https://echo-trail-api.onrender.com`：

1. 访问`/api/v1/health`，检查`database`和`storage`是否均为`connected`。
2. 访问`/docs`，确认Swagger接口页可打开。
3. 创建匿名会话，查询广东和陕西歌曲。
4. 上传一张测试图片，确认返回的是COS地址且可以访问。
5. 完成一次播放记录、烫银票根生成和票根列表查询。

## 5. 免费方案注意事项

- Render免费Web Service长时间无访问后可能休眠，第一次打开需要等待冷启动。
- Render免费PostgreSQL不适合长期保存重要数据，必须在控制台确认当前有效期和限制。
- COS按实际存储量和流量计费，上线前建议设置预算提醒。
- 修改GitHub `main`分支后Render会自动重新部署，上线前应先运行全部测试。
