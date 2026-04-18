# 📚 文档问答助手

一个基于 RAG（检索增强生成）的文档问答系统。用户上传文档后，可以用自然语言提问，系统基于文档内容智能回答，并标注答案来源。

## ✨ 功能特点

- 📄 **文档上传**：支持上传任意 txt 格式文档
- 🔍 **语义搜索**：基于向量数据库的语义检索，不只是关键词匹配
- 🤖 **智能问答**：调用 Claude 大模型根据文档内容生成准确回答
- 📌 **来源追溯**：每个回答都标注依据的原文段落
- 💬 **多轮对话**：保留聊天历史，支持连续提问
- 🚫 **拒绝幻觉**：文档里没有的内容会诚实回答"无法回答"

## 🛠 技术栈

- **后端**：Python 3.13 + FastAPI
- **前端**：Streamlit
- **向量数据库**：ChromaDB
- **大模型**：Claude (Anthropic API)

## 📁 项目结构
├── doc_api.py       # FastAPI 后端：文档处理 + 问答接口
├── web.py           # Streamlit 前端：用户交互界面
├── test_doc.txt     # 测试用文档
└── README.md        # 说明文档


## 🚀 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn streamlit chromadb anthropic python-multipart requests
```

### 2. 配置 API Key

设置环境变量：
```bash
setx ANTHROPIC_AUTH_TOKEN "your-api-key"
setx ANTHROPIC_BASE_URL "your-api-endpoint"
```

### 3. 启动后端

```bash
python -m uvicorn doc_api:app --reload
```

后端会运行在 `http://127.0.0.1:8000`

### 4. 启动前端

新开一个终端：
```bash
python -m streamlit run web.py
```

前端会自动打开浏览器，访问 `http://localhost:8501`

## 💡 使用方法

1. 在前端界面上传 txt 文档
2. 点击"上传到系统"按钮
3. 在底部输入框提问
4. 查看回答和原文来源

## 🏗 系统架构
用户 → Streamlit 前端 → FastAPI 后端 → ChromaDB (语义检索)
↓
Claude API (生成回答)

## 📝 核心流程

**文档处理流程：**
1. 读取上传的文本文件
2. 按空行切分为段落
3. 存入 ChromaDB 向量数据库（自动生成 embedding）

**问答流程：**
1. 用户输入问题
2. 向量搜索最相关的 2 个段落
3. 将段落作为上下文，连同问题发送给 Claude
4. 返回答案 + 来源段落

## 🔧 可优化方向

- [ ] 支持 PDF 格式上传
- [ ] 更智能的文档切分（按语义而非空行）
- [ ] 流式输出回答（打字机效果）
- [ ] 多文档支持
- [ ] 用户账户系统

## 📄 License

MIT