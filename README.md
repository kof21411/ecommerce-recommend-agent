# 电商推荐 Agent

基于多智能体协作与 RAG 的电商推荐系统。

- 后端：Python / FastAPI / LangChain / ChromaDB
- 前端：Vue 3 / TypeScript / Vite / Pinia / Element Plus
- 数据：PostgreSQL 15 / Redis 7 / ChromaDB

## 功能

- 智能对话推荐（SSE 流式响应）
- 语义商品搜索（RAG + 向量相似度）
- 个性化推荐与推荐理由
- 商品咨询问答、商品对比
- 商品列表筛选、排序、分页
- JWT 注册 / 登录

## 项目结构

```
ecommerce-recommend-agent/
├── backend/
│   ├── main.py / config.py / database.py / models.py / schemas.py / auth.py
│   ├── api/          # auth / products / chat / recommend
│   ├── agents/       # orchestrator / search / recommend / critic / qa
│   ├── rag/          # embeddings / vector_store / retriever
│   └── services/     # product_service / user_service
├── frontend/
│   └── src/          # views / components / stores / api / router
├── database.sql
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.conf
```

## 快速启动（Docker）

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

docker compose up -d --build
```

访问：

- 前端：<http://localhost>
- API 文档：<http://localhost:8000/docs>
- ChromaDB：<http://localhost:8001>

## 本地开发

1. 启动依赖服务：

```bash
docker compose up -d postgres redis chromadb
```

2. 后端：

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env   # 修改 DATABASE_URL / REDIS_URL / CHROMA_HOST 为 localhost
uvicorn main:app --reload --port 8000
```

3. 前端：

```bash
cd frontend
npm install
npm run dev
```

访问 <http://localhost:5173>。Vite 已将 `/api` 代理到 `http://localhost:8000`。

## 环境变量

商品创建和索引重试需要在 `.env` 中设置 `PRODUCT_MANAGER_EMAILS=["admin@example.com"]`。先通过可信方式创建并核验管理员账户，再配置白名单；白名单邮箱不能通过公开注册创建。创建商品后同步尝试索引；失败时可调用 `POST /api/products/{id}/index` 重试。人工全量重建：在 `backend` 目录运行 `python -m scripts.sync_vectors --mode full`，执行期间避免并发商品写入。

管理员可使用 `PATCH /api/products/{id}` 更新、`POST /api/products/{id}/deactivate` 下架、`DELETE /api/products/{id}` 软删除商品。数据库先提交，响应的 `index_status=failed` 表示索引同步失败，需手动重试或执行全量对账；下架及删除记录不会参与推荐。

见 [.env.example](.env.example)。关键项：

| 变量 | 说明 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI API Key（必填） |
| `DATABASE_URL` | PostgreSQL 异步连接串 |
| `REDIS_URL` | Redis 连接串 |
| `CHROMA_HOST` / `CHROMA_PORT` | ChromaDB 地址 |
| `SECRET_KEY` | JWT 签名密钥，生产环境务必修改 |

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/me` | 当前用户 |
| GET | `/api/products/` | 商品列表（筛选/排序/分页） |
| GET | `/api/products/{id}` | 商品详情 |
| GET | `/api/products/categories/list` | 分类列表 |
| POST | `/api/recommend/` | 个性化推荐（非流式） |
| POST | `/api/chat/` | 对话（SSE 流式） |
| GET | `/api/chat/history` | 对话历史 |
| GET | `/health` | 健康检查 |

除注册/登录/健康检查外，其余接口需要 `Authorization: Bearer <token>`。

## 说明

- 首次启动时 `database.sql` 只会写入分类和知识库文档，不会生成商品数据；可通过 SQL 或自行扩展接口写入商品后再浏览。
- `database.sql` 与 SQLAlchemy `create_all` 均会建表，重复执行时以数据库初始化脚本为准。
- 商品语义检索依赖 ChromaDB 中已写入的 `product_knowledge` 集合；集合为空时不会返回语义商品候选。Chroma 不可用时尝试数据库关键词降级。
- 聊天与推荐依赖 OpenAI API；未配置有效 Key 时，相关接口会返回错误。
