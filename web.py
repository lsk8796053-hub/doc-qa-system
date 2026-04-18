"""
文档问答系统 - 前端界面
基于 Streamlit 的聊天式交互界面

调用后端 FastAPI 接口实现文档上传和问答功能
"""

import streamlit as st
import requests

# ========== 配置 ==========
API_URL = "http://127.0.0.1:8000"

# 页面设置
st.set_page_config(
    page_title="文档问答助手",
    page_icon="📚",
    layout="centered"
)

st.title("📚 文档问答助手")
st.caption("上传文档，然后用自然语言提问")


# ========== 初始化对话历史 ==========
if "history" not in st.session_state:
    st.session_state.history = []


# ========== 文档上传区域 ==========
st.subheader("1. 上传文档")
uploaded_file = st.file_uploader("选择一个文本文件", type=["txt"])

if uploaded_file is not None:
    if st.button("上传到系统"):
        # 把文件发送到后端 /upload 接口
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")
        }
        response = requests.post(f"{API_URL}/upload", files=files)
        result = response.json()
        st.success(f"✅ 上传成功！文档切分成 {result['chunks']} 段")
        # 上传新文档时清空旧的对话历史
        st.session_state.history = []


st.divider()


# ========== 对话区域 ==========
st.subheader("2. 开始对话")

# 显示历史对话
for item in st.session_state.history:
    with st.chat_message("user"):
        st.write(item["question"])
    with st.chat_message("assistant"):
        st.write(item["answer"])
        with st.expander("查看来源"):
            for chunk in item["sources"]:
                st.info(chunk)

# 底部输入框
question = st.chat_input("请输入你的问题...")

if question:
    # 显示用户问题
    with st.chat_message("user"):
        st.write(question)
    
    # 显示 AI 回答（带加载动画）
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            response = requests.post(
                f"{API_URL}/ask",
                json={"text": question}
            )
            result = response.json()
        
        st.write(result["answer"])
        with st.expander("查看来源"):
            for chunk in result["sources"]:
                st.info(chunk)
    
    # 保存到历史记录
    st.session_state.history.append({
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"]
    })