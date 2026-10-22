"""
用 LangChain 重写文档问答的最简版本
不含 FastAPI 和前端，一个脚本跑完：读文件 → 切分 → 向量化入库 → 检索 → 回答

运行前提：在 doc-qa-system 文件夹、venv 已激活、test_doc.txt 在同一文件夹
启动：python lc_rag.py
"""

import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# ========== 1. 读文件 ==========
# 原版：await file.read() 再 decode("utf-8")
with open("test_doc.txt", encoding="utf-8") as f:
    content = f.read()


# ========== 2. 切分 ==========
# 原版：content.split("\n\n") + 自己写的标题合并
# 这里：先按空行切，太长再按换行切，再不行按句号切；
#      切完会把相邻的小块合并，直到接近 chunk_size
splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "。"],
    chunk_size=100,      # 每段最多约 100 个字
    chunk_overlap=0,     # 相邻段之间重叠的字数，先设为 0
)
chunks = splitter.split_text(content)

print(f"切分成 {len(chunks)} 段：")
for i, c in enumerate(chunks):
    print(f"--- 第 {i} 段 ---\n{c}")
print("=" * 40)


# ========== 3. 向量化 + 存入向量库 ==========
# 原版：SentenceTransformerEmbeddingFunction + chromadb 的 create_collection / add
# 这里：不写 persist_directory，只存在内存里，脚本结束就清空，不影响原来的 chroma_db
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma.from_texts(chunks, embedding=embeddings)


# ========== 4. 检索器 ==========
# 原版：collection.query(query_texts=[...], n_results=2)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})


# ========== 5. Prompt 模板 ==========
# 原版：f-string 拼 prompt
prompt = ChatPromptTemplate.from_template(
    """根据下面的文档回答问题，不要编造文档以外的内容，不要使用任何Markdown格式。

文档：
{context}

问题：{question}"""
)


# ========== 6. 大模型 ==========
# 原版：OpenAI(...) + ai_client.chat.completions.create(...)
llm = ChatOpenAI(
    model="gpt-6.1-sol",
    api_key=os.environ["GPT_RELAY_KEY"],
    base_url=os.environ["GPT_RELAY_URL"],
    timeout=30,
)


# ========== 7. 把上面几步串成一条链 ==========
# 原版：在 ask() 函数里按顺序手动调用每一步
def format_docs(docs):
    """把检索到的文档对象拼成一段文字。原版：'\\n\\n'.join(relevant_chunks)"""
    return "\n\n".join(d.page_content for d in docs)


chain = (
    {
        "context": retriever | format_docs,   # 问题 → 检索 → 拼成文字
        "question": RunnablePassthrough(),    # 问题原样传下去
    }
    | prompt                # 填进模板
    | llm                   # 交给大模型
    | StrOutputParser()     # 只取出回答的文字
)


# ========== 8. 提问 ==========
for q in ["请假流程是什么？", "报销超过2000元找谁审批？"]:
    print("问：", q)
    print("答：", chain.invoke(q))
    print("-" * 40)
