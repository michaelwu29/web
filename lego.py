import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from webster import extract_invoice_data

st.set_page_config(page_title="发票提取器", layout="centered")
st.title("📄 发票提取器")

# Initialize session state storage
if "invoice_data" not in st.session_state:
    st.session_state.invoice_data = []

uploaded_files = st.file_uploader("📤 上传多个 PDF 发票文件", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            with open("temp_invoice.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())

        data = extract_invoice_data("temp_invoice.pdf")
        data["文件名"] = uploaded_file.name
        st.session_state.invoice_data.append(data)

    st.success(f"✅ 已添加 {len(uploaded_files)} 份发票数据")

if st.session_state.invoice_data:
    df = pd.DataFrame(st.session_state.invoice_data)
    st.subheader("📋 当前累计的发票信息：")
    st.dataframe(df)

    # Download as CSV
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 下载累计发票数据为 CSV",
        data=csv,
        file_name="invoice_data_all.csv",
        mime="text/csv"
    )

    # Clear button
    if st.button("🗑️ 清空所有已上传数据"):
        st.session_state.invoice_data = []
        st.success("数据已清空。")
