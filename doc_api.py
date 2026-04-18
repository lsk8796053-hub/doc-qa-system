"""
文档问答系统 - 后端 API
基于 RAG(检索增强生成)的文档问答服务

功能：
1. 上传文本文件，自动切分并存入向量数据库
2. 接收用户问题，搜索相关段落并由 AI 回答
"""

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import chromadb
import anthropic

# ========== 初始化 ==========
app = FastAPI(title="文档问答系统", description="基于 RAG 的文档问答 API")

# 向量数据库客户端（存储切分后的文档）
db_client = chromadb.Client()

# AI 客户端（调用大模型回答问题）
ai_client = anthropic.Anthropic()


# ========== 数据模型 ==========
class Question(BaseModel):
    """用户提问的数据结构"""
    text: str


# ========== 接口 ==========
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    上传文档接口
    
    流程：
    1. 读取上传的文件内容
    2. 按空行切分为多个段落
    3. 清空旧数据，存入新数据到向量数据库
    """
    # 读取文件内容
    content_bytes = await file.read()
    content = content_bytes.decode("utf-8")
    
    # 处理 Windows 换行符后按空行切分段落
    content = content.replace("\r\n", "\n")
    chunks = content.split("\n\n")
    chunks = [c.strip() for c in chunks if c.strip()]
    
    # 清空旧数据，重建集合
    try:
        db_client.delete_collection("my_docs")
    except:
        pass
    new_collection = db_client.create_collection("my_docs")
    
    # 存入向量数据库，每段分配一个唯一 ID
    new_collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    
    return {
        "message": "上传成功",
        "filename": file.filename,
        "chunks": len(chunks)
    }


@app.post("/ask")
def ask(q: Question):
    """
    问答接口
    
    流程：
    1. 从向量数据库搜索最相关的 2 段内容
    2. 把相关内容作为上下文传给 AI
    3. AI 根据上下文回答问题
    """
    # 获取向量数据库集合
    collection = db_client.get_or_create_collection("my_docs")
    
    # 搜索最相关的 2 段
    results = collection.query(
        query_texts=[q.text],
        n_results=2
    )
    relevant_chunks = results["documents"][0]
    
    # 拼接为上下文
    context = "\n\n".join(relevant_chunks)
    
    # 调用 AI 回答
    response = ai_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""根据下面的文档回答问题，不要编造文档以外的内容，不要使用任何Markdown格式。

文档：
{context}

问题：{q.text}"""
        }]
    )
    
    return {
        "question": q.text,
        "answer": response.content[0].text,
        "sources": relevant_chunks
    }