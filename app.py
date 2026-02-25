# import streamlit as st
# import requests
# import uuid

# st.set_page_config(page_title="Job AI Assistant", page_icon="🤖")

# API_CHAT = "http://localhost:8000/chat"
# API_RESET = "http://localhost:8000/reset"

# st.title("🤖 Job Intelligence Assistant")

# # =========================
# # 🎛 Result Settings
# # =========================
# top_k = st.slider(
#     "Jumlah lowongan ditampilkan",
#     min_value=1,
#     max_value=20,
#     value=5
# )

# # =========================
# # 1️⃣ Generate user_id per session
# # =========================
# if "user_id" not in st.session_state:
#     st.session_state.user_id = str(uuid.uuid4())

# # =========================
# # 2️⃣ Reset Button
# # =========================
# col1, col2 = st.columns([6, 1])

# with col2:
#     if st.button("Reset"):
#         requests.post(
#             API_RESET,
#             params={"user_id": st.session_state.user_id}
#         )
#         st.session_state.messages = []
#         st.rerun()

# # =========================
# # 3️⃣ Chat history
# # =========================
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # =========================
# # 4️⃣ User input
# # =========================
# if prompt := st.chat_input("Tanya soal lowongan kerja..."):

#     # Simpan user message
#     st.session_state.messages.append({
#         "role": "user",
#         "content": prompt
#     })

#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # =========================
#     # 5️⃣ Call backend
#     # =========================
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):

#             response = requests.post(
#                 API_CHAT,
#                 json={
#                     "user_id": st.session_state.user_id,
#                     "user_input": prompt,
#                     "top_k": top_k   # 🔥 kirim ke backend
#                 }
#             )

#             data = response.json()

#             answer = data.get("answer", "Terjadi kesalahan.")
#             token_usage = data.get("token_usage", {})
#             tool_calls = data.get("tool_calls", [])

#             st.markdown(answer)

#             # 🔹 Tampilkan token kecil di bawah jawaban
#             if token_usage:
#                 st.caption(
#                     f"🪙 Tokens: {token_usage.get('total_tokens', 0)}"
#                 )

#             # 🔹 Optional: tampilkan tool yang dipakai
#             if tool_calls:
#                 with st.expander("🛠 Tool Used"):
#                     st.json(tool_calls)

#     # Simpan jawaban AI
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": answer
#     })


import streamlit as st
import requests
import uuid

st.set_page_config(page_title="Job AI Assistant", page_icon="🤖")

API_CHAT = "http://localhost:8000/chat"
API_RESET = "http://localhost:8000/reset"
API_UPLOAD = "http://localhost:8000/upload-cv"

st.title("🤖 Job Intelligence Assistant")

# =========================
# 🎛 Result Settings
# =========================
top_k = st.slider(
    "Jumlah lowongan ditampilkan",
    min_value=1,
    max_value=20,
    value=5
)

# =========================
# 🪙 Token Counter
# =========================
if "total_tokens_used" not in st.session_state:
    st.session_state.total_tokens_used = 0

# =========================
# 📊 Sidebar
# =========================
with st.sidebar:
    st.header("📊 Session Info")
    st.metric(
        label="Total Tokens Used",
        value=st.session_state.total_tokens_used
    )

# =========================
# 1️⃣ Generate user_id per session
# =========================
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# =========================
# 2️⃣ Reset Button
# =========================
col1, col2 = st.columns([6, 1])

with col2:
    if st.button("Reset"):
        requests.post(
            API_RESET,
            params={"user_id": st.session_state.user_id}
        )
        st.session_state.messages = []
        st.session_state.total_tokens_used = 0
        st.rerun()

# =========================
# 📄 CV Upload Section
# =========================
st.divider()
st.subheader("📄 Upload CV untuk Rekomendasi")

uploaded_file = st.file_uploader(
    "Upload CV (PDF)",
    type=["pdf"]
)

if uploaded_file:
    if st.button("🔎 Cari Lowongan dari CV"):

        with st.spinner("Menganalisis CV..."):

            response = requests.post(
                API_UPLOAD,
                files={"file": uploaded_file},
                params={"k": top_k}
            )

            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])

                if recommendations:
                    st.success(f"Ditemukan {len(recommendations)} lowongan cocok")

                    for idx, job in enumerate(recommendations, start=1):
                        with st.container():
                            st.markdown(f"### {idx}. {job['job_title']}")
                            st.write(f"🏢 {job['company_name']}")
                            st.write(f"📍 {job['location']}")
                            st.write(f"💼 {job['work_type']}")
                            st.write(f"💰 {job['salary']}")
                            st.write(f"🎯 Match Score: {job['match_score']}")
                            st.markdown("---")
                else:
                    st.warning("Tidak ditemukan lowongan yang cocok.")
            else:
                st.error("Gagal memproses CV.")

# =========================
# 💬 Chat Section
# =========================
st.divider()
st.subheader("💬 Tanya Seputar Lowongan")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Tanya soal lowongan kerja..."):

    # Simpan user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            response = requests.post(
                API_CHAT,
                json={
                    "user_id": st.session_state.user_id,
                    "user_input": prompt,
                    "top_k": top_k
                }
            )

            data = response.json()

            answer = data.get("answer", "Terjadi kesalahan.")
            token_usage = data.get("token_usage", {})
            tool_calls = data.get("tool_calls", [])

            st.markdown(answer)

            # 🔥 Tambah token ke sidebar
            if token_usage:
                used = token_usage.get("total_tokens", 0)
                st.session_state.total_tokens_used += used
                st.caption(f"🪙 Tokens used (this message): {used}")

            # Optional: tool info
            if tool_calls:
                with st.expander("🛠 Tool Used"):
                    st.json(tool_calls)

    # Simpan jawaban AI
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })