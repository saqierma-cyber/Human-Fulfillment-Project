# 人类补完计划

[![README in English](https://img.shields.io/badge/README-English-blue?style=for-the-badge)](./README.md)
[![项目愿景](https://img.shields.io/badge/项目-人类补完计划-111827?style=for-the-badge)](./Human%20Fulfillment%20Project%EF%BC%88%E4%BA%BA%E7%B1%BB%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92%EF%BC%89%E9%A1%B9%E7%9B%AE%E8%AF%B4%E6%98%8E.md)
[![状态](https://img.shields.io/badge/状态-本地MVP-orange?style=for-the-badge)](https://github.com/saqierma-cyber/Human-Fulfillment-Project)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.44-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MiniMax](https://img.shields.io/badge/大模型-MiniMax-5B5BD6?style=for-the-badge)](https://platform.minimaxi.com/)

## 项目愿景

**Human Fulfillment Project（人类补完计划）** 的出发点很直接：个体生命有限，但人类智慧是可以积累、继承、调用的。  
与其让每个人都独自重复前人经历过的迷茫、错误与遗憾，不如把古人的智慧、老师和思想者的洞见，以及普通人的人生经验，借助 AI 整理成可调用的辅助系统，用来支持现实生活中的关键判断与选择。

这个仓库就是这个大方向下的一个开源 MVP 组件。  
它聚焦于：用曾仕强相关书籍构成本地知识库，再结合检索与大模型分析，去理解职场和家庭场景中的复杂事件。

完整项目说明见：
- [Human Fulfillment Project（人类补完计划）项目说明](./Human%20Fulfillment%20Project%EF%BC%88%E4%BA%BA%E7%B1%BB%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92%EF%BC%89%E9%A1%B9%E7%9B%AE%E8%AF%B4%E6%98%8E.md)

## 这个仓库是什么

这是一个基于曾仕强著作语料构建的**本地 RAG 分析 MVP**。

用户输入一个现实事件后，系统会尽量完成以下过程：
- 识别问题主题
- 从本地书库中检索相关内容
- 拆解人物、关系、前因后果与关键矛盾
- 以曾仕强视角组织分析
- 预判后续走向
- 给出建议，并尽可能附带引用依据

当前重点场景：
- 职场
- 家庭关系

## 这个开源版包含什么

开源版包含：
- 后端服务代码
- Streamlit 本地界面
- 文档导入脚本
- OCR 补录脚本
- 数据库导出和调试脚本
- Prompt 模板
- 环境变量模板
- 项目说明文档

开源版不包含：
- 你的私有电子书语料
- 本地导出的数据库结果
- 本地虚拟环境
- 私有 `.env`
- 真实 MiniMax API Key

## 目录结构

```text
Human-Fulfillment-Project/
├── app/                         # FastAPI 后端
│   ├── api/                     # 问答/管理路由
│   ├── core/                    # 配置与提示词
│   ├── db/                      # 数据库模型与连接
│   └── services/                # 解析、OCR、检索、分析
├── ui/                          # Streamlit 本地界面
├── scripts/                     # 导入、OCR、导出、调试脚本
├── prompts/                     # 提示词模板
├── data/                        # 数据目录占位
├── docker-compose.yml           # PostgreSQL + pgvector
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
└── README.zh-CN.md
```

## 技术栈

| 层级 | 技术 |
|---|---|
| 后端 | FastAPI |
| 前端 | Streamlit |
| 数据库 | PostgreSQL + pgvector |
| 文档解析 | PyMuPDF、ebooklib |
| OCR | pytesseract + 本地 tesseract |
| 大模型集成 | MiniMax（OpenAI 兼容方式） |
| 运行环境 | Python 3.12 |
| 本地基础设施 | Docker Compose |

## 工作流程

1. 解析本地 `PDF / EPUB / TXT` 文档。
2. 对扫描版 PDF 做 OCR 补录。
3. 将文档切分为可检索的文本块。
4. 把文档元数据和 chunk 存入 PostgreSQL。
5. 对用户输入做主题分类。
6. 从本地书库中检索相关段落。
7. 调用 MiniMax 做结构化分析。
8. 如果模型结构化失败，则回退到本地规则分析。
9. 在 Streamlit 本地界面展示结果。

## 当前状态

- 本地 MVP 已经可以运行。
- OCR 补录链路已接通。
- 数据库导出 JSONL 已实现，便于人工检查。
- MiniMax 兼容性已优化，启用了 `reasoning_split=True`。
- OpenAI 兼容客户端已通过 `trust_env=False` 避免代理干扰。
- 本地界面已支持结构化分析展示。
- 语义 embedding 检索在这个公开版本中还未启用。

## 快速开始

### 1. 创建环境变量文件

```bash
cp .env.example .env
```

然后在 `.env` 中填入你自己的 MiniMax 配置。

### 2. 启动 PostgreSQL

```bash
docker compose up -d
```

### 3. 创建 Python 3.12 虚拟环境

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. 可选：安装 OCR 依赖

```bash
brew install tesseract tesseract-lang
```

然后在 `.env` 中启用 OCR。

### 5. 导入文档

```bash
python scripts/ingest_books.py
```

如果之前有扫描版 PDF 被导成 `zero-chunk`：

```bash
python scripts/reingest_zero_chunk_docs.py
```

### 6. 启动后端

```bash
uvicorn app.main:app --reload
```

### 7. 启动本地界面

```bash
streamlit run ui/streamlit_app.py
```

## 适合的问题

- 明确的职场权力与协作问题
- 明确人物关系的家庭冲突
- 亲子与代际张力
- 人际沟通和情绪管理问题
- 前因、关系、决策张力都比较明确的问题

## 不适合的问题

- 过度抽象的人生哲学提问
- 医疗、法律、税务、投资等专业意见
- 强时间敏感的事实查询
- 没有清晰人物和冲突结构的问题
- 需要通用型万能助手能力的问题

## 当前不完美的地方

- 检索目前仍以关键词和规则为主。
- 主题分类仍然依赖人工整理的词表。
- 模型结构化输出有时会失败，触发本地回退分析。
- 引用还是 chunk 级，不是严格段落级。
- 大合集文档仍可能影响检索质量。
- 公开仓库不包含实际书库语料。

## 后续方向

- 扩充家庭与职场冲突的主题词表
- 启用 embedding 语义检索
- 提高结构化输出成功率
- 继续优化前端展示
- 提高引用精度
- 建立更好的评估案例集

## 开源使用说明

- 请使用你自己合法获取的原始文档。
- 请使用你自己的 MiniMax API Key。
- 这个仓库首先面向**本地单机使用**，不是公开多用户部署版本。
- 仓库中的 `.env.example` 保留了配置结构，但不会暴露私有凭证。

