# 文档问答系统（RAG + Agent）

上传文本文档后，用自然语言提问，系统从文档中检索相关段落，再由大模型基于这些段落回答，并展示答案的来源段落。在此基础上扩展了 Agent 功能，并用 LangChain 重构了检索问答流程。

## 功能

- **文档入库**：上传 txt 文件，按段落切分，并把短标题合并到下一段正文开头；用中文 Embedding 模型 BGE-small-zh 向量化后存入 ChromaDB。
- **检索问答**：问题向量化后检索最相似的段落，按相似度阈值过滤掉无关内容；没有相关内容时直接返回“未找到”，不调用大模型。
- **控制幻觉**：在 Prompt 中要求模型只根据检索到的内容回答，并返回来源段落，方便核对。
- **Agent**：基于 Function Calling，把文档检索（`search_docs`）和时间查询（`get_time`）封装成工具，由模型自主决定是否调用、调用哪个；支持一次并行调用多个工具，并设置最大步数防止无限循环。
- **LangChain 版本**：用 LangChain 的切分器、向量库、检索器、Prompt 模板和 LCEL 链式写法重写了同一套流程。

## 技术栈

Python、FastAPI、Streamlit、ChromaDB、sentence-transformers（BGE-small-zh）、OpenAI 兼容 API、LangChain

## 项目结构

| 文件 | 说明 |
|---|---|
| `doc_api.py` | 后端：`/upload` 文档入库，`/ask` 检索问答 |
| `web.py` | 前端：Streamlit 聊天界面 |
| `agent.py` | Agent 版本：模型自主调用检索和时间工具 |
| `lc_rag.py` | LangChain 重构版本（单脚本，不含前后端） |
| `requirements.txt` | 依赖列表 |

## 运行方法

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量（OpenAI 兼容接口的 key 和地址）
export GPT_RELAY_KEY="你的 key"
export GPT_RELAY_URL="接口地址"

# 4. 启动后端和前端（两个终端）
python -m uvicorn doc_api:app --port 8000
python -m streamlit run web.py

# 5. 其他版本
python agent.py      # Agent 版（需先通过前端上传过文档）
python lc_rag.py     # LangChain 版（读取同目录下的 test_doc.txt）
```

模型名称在代码中设置，可按所用接口自行修改。

## 开发中遇到的问题

1. **中文检索排序错误**：ChromaDB 默认的 Embedding 模型以英文为主，问“请假流程”时，排在第一的却是“报销流程”。查看返回的来源段落后确认是检索出了问题，改用中文模型 BGE-small-zh 后排序恢复正确。
2. **标题被单独切成一段**：按空行切分时，标题会单独成段。检索只取两段，标题段排名靠前却没有实际信息，浪费了一个名额。加入合并逻辑后，每段都是“标题 + 正文”。
3. **固定 top-k 会凑数**：即使排序正确，top-k 也一定会返回 k 段，不相关的内容会被拿来凑数。打印检索距离后发现，相关段约为 0.31，无关段在 0.5 以上，于是设定阈值 0.45 进行过滤。
4. **通用切分器不理解文档结构**：LangChain 的 RecursiveCharacterTextSplitter 按长度贪心合并，会把下一节的标题拼到上一段末尾。说明切分最好结合文档自身的结构，例如 Markdown 标题。

## 不足与改进方向

- 目前每次上传会清空旧数据，只支持单个 txt 文档；可以为每段增加来源文件等元数据，支持多文档管理和按文件更新。
- 标题判断依赖字数等规则，容易误判；可以改用 Markdown、Word 等文档自带的标题结构切分。
- 阈值只用少量问题测定；应准备测试集，分别评估检索命中率和回答质量。
- 可以尝试混合检索（向量 + 关键词）和重排序（rerank）来进一步提升检索效果。
