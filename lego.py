import fitz  # PyMuPDF
import re
import pandas as pd
import os
import streamlit as st

st.set_page_config(page_title="📄 Chinese Invoice Extractor", layout="centered")
st.title("📄 Chinese Invoice Extractor")

# Initialize session state to store multiple invoice results
if "invoice_data" not in st.session_state:
    st.session_state.invoice_data = []

# File uploader for multiple PDFs
uploaded_files = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

# Blacklist to avoid mis-extraction
label_blacklist = [
    "规格型号", "单位", "数量", "单 价", "金 额", "税率", "征收率", "税  额",
    "项目名称", "合计", "价税合计", "订单号", "开票人", "名 称", "统一社会信用代码",
    "纳税人识别号", "数 量", "电子发票(普通发票)", '税率/征收率', '价税合计(写)', 
    '单 位', '税 额', '西迪斯（天津）电子', '西迪斯（天津）电子有限公司'
]

# Extraction function
def extract_invoice_data(pdf_path):
    invoice_number = None
    invoice_date = None
    company_name = None
    expect_invoice_number = False
    expect_invoice_date = False

    doc = fitz.open(pdf_path)
    lines = []
    for page in doc:
        text = page.get_text()
        lines += text.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()

        if "发票号码" in line:
            expect_invoice_number = True
            continue
        elif "开票日期" in line:
            expect_invoice_date = True
            continue

        # Extract 发票号码
        if expect_invoice_number and re.fullmatch(r"\d{18,20}", line):
            invoice_number = line
            expect_invoice_number = False

        # Extract 开票日期
        if expect_invoice_date:
            match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", line)
            if match:
                y, m, d = match.groups()
                invoice_date = f"{y}/{m.zfill(2)}/{d.zfill(2)}"
                expect_invoice_date = False

        # Extract 名称 that contains 有限公司 and not in blacklist
        if "有限公司" in line and not company_name:
            if not any(label in line for label in label_blacklist):
                company_name = line.strip()

    return {
        "发票号码": invoice_number,
        "开票日期": invoice_date,
        "名称": company_name
    }

# Process uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        with open("temp_invoice.pdf", "wb") as f:
            f.write(uploaded_file.read())

        result = extract_invoice_data("temp_invoice.pdf")
        result["文件名"] = uploaded_file.name
        st.session_state.invoice_data.append(result)

    st.success(f"✅ Processed {len(uploaded_files)} file(s).")

# Display extracted data
if st.session_state.invoice_data:
    df = pd.DataFrame(st.session_state.invoice_data)
    st.subheader("📋 Extracted Invoice Data:")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8-sig")

    # Download button
    st.download_button(
        label="📥 Download All as CSV",
        data=csv,
        file_name="invoice_data_all.csv",
        mime="text/csv"
    )

    # Clear session state
    if st.button("🗑️ Clear Uploaded Data"):
        st.session_state.invoice_data = []
        st.success("Cleared all uploaded data.")
