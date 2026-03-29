# data 目录说明

- `raw/`：原始文档副本或符号链接
- `parsed/`：解析出的纯文本
- `chunks/`：切块结果
- `exports/`：导出的调试文件
- `cache/`：运行缓存

MVP 默认直接读取 `.env` 中的 `BOOK_SOURCE_DIR`，不强制复制原书到本目录。

当前项目可用下面的脚本把 PostgreSQL 里的文本化结果导出到本目录：

```bash
python scripts/export_db_to_jsonl.py
```

说明：
- `chunks/` 是数据库中真实存储的检索块导出，最值得优先检查。
- `parsed/` 不是原始 parse 结果的完整回放，而是按 `page_label` 对 chunk 聚合出的近似页视图。
- `exports/documents_manifest.jsonl` 会列出每本书对应的导出文件路径与条数。
