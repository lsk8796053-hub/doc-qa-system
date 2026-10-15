"""
文档问答 Agent
在项目一的基础上，让模型自己决定：要不要检索文档、检索什么、要不要查时间

运行前提：
    - 在 doc-qa-system 文件夹里运行（要用到同一个 chroma_db）
    - 之前已经通过 /upload 上传过文档
    - 环境变量 GPT_RELAY_KEY、GPT_RELAY_URL 已设置
启动：python agent.py
"""

import os
import json
from datetime import datetime

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from openai import OpenAI

# ========== 初始化 ==========
client = OpenAI(api_key=os.environ["GPT_RELAY_KEY"], base_url=os.environ["GPT_RELAY_URL"])
MODEL = "gpt-6.1-sol"   # 和 doc_api.py 用同一个模型

db = chromadb.PersistentClient(path="chroma_db")
ef = SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-zh-v1.5")
collection = db.get_or_create_collection("my_docs", embedding_function=ef)


# ========== 工具：真正干活的函数 ==========
def get_time():
    """返回当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def search_docs(query):
    """在文档里检索，沿用项目一的阈值过滤"""
    results = collection.query(query_texts=[query], n_results=2)
    docs = results["documents"][0]
    dists = results["distances"][0]
    hits = [d for d, dist in zip(docs, dists) if dist < 0.45]
    return "\n\n".join(hits) if hits else "文档中没有找到相关内容"


# 名字 → 函数 的对照表：模型说要调用哪个名字，就从这里找到对应的函数
TOOL_FUNCS = {
    "get_time": get_time,
    "search_docs": search_docs,
}

# ========== 工具说明书：给模型看的 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前的真实时间",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "在用户上传的公司文档中检索相关内容，例如请假、报销、餐厅等制度",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "检索关键词"}},
                "required": ["query"],
            },
        },
    },
]


# ========== Agent 循环 ==========
def run_agent(question, max_steps=5):
    messages = [
        {
            "role": "system",
            "content": "你是公司文档助手。涉及公司制度的问题，先用 search_docs 检索，只根据检索结果回答；"
                       "问时间用 get_time；闲聊直接回答。不要使用 Markdown 格式。",
        },
        {"role": "user", "content": question},
    ]

    for step in range(max_steps):          # 最多循环 max_steps 次，防止失控
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        msg = resp.choices[0].message

        # 模型没有申请工具 → 说明它准备好回答了，循环结束
        if not msg.tool_calls:
            return msg.content

        # 模型申请了工具 → 先把申请单原样放回对话
        messages.append(msg)

        # 可能一次申请多个工具，逐个执行
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            print(f"  [第{step + 1}步] 调用 {tc.function.name}，参数 {args}")
            result = TOOL_FUNCS[tc.function.name](**args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
        # 带着工具结果，回到循环开头，再问一次模型

    return "步骤过多，已停止。"


if __name__ == "__main__":
    questions = [
        "请假流程是什么？",
        "现在几点？",
        "你好",
        "现在几点了？另外报销超过2000元要找谁审批？",
    ]
    for q in questions:
        print("问：", q)
        print("答：", run_agent(q))
        print("-" * 40)
