import fitz  # PyMuPDF
import re
import pandas as pd
import os
import streamlit as st
st.title("📄 Chinese Invoice Extractor")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    st.success("PDF uploaded successfully!")

    # Save the file temporarily
    with open("temp_invoice.pdf", "wb") as f:
        f.write(uploaded_file.read())



    def save_to_csv(data, csv_path="/Users/michaelwu/Downloads/invoices_chinese.csv"):
        df = pd.DataFrame([data])
        if not os.path.exists(csv_path):
            df.to_csv(csv_path, index=False)
            print(f"Created new CSV: {csv_path}")
        else:
            df.to_csv(csv_path, mode='a', index=False, header=False)
            print(f"Appended to CSV: {csv_path}")
    def extract_invoice_data(pdf_path):
        invoice_number = None
        invoice_date = None
        company_name = None

        expect_invoice_number = False
        expect_invoice_date = False
        expect_company_name = False

        # Open PDF with fitz (PyMuPDF)
        doc = fitz.open(pdf_path)
        lines = []
        label_blacklist = [
            "规格型号", "单位", "数量", "单 价", "金 额", "税率", "征收率", "税  额",
            "项目名称", "合计", "价税合计", "订单号", "开票人", "名 称", "统一社会信用代码", "纳税人识别号", "数 量",
            "电子发票(普通发票)", '税率/征收率', '价税合计(写)', '单 位', '税 额',' 西迪斯（天津）电子','西迪斯（天津）电子有限公司'
        ]
        for page in doc:
            text = page.get_text()
            lines += text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Set flags when labels are found
            if "发票号码" in line:
                expect_invoice_number = True
                continue
            elif "开票日期" in line:
                expect_invoice_date = True
                continue
            if "有限公司" in line and not company_name:
                if not any(label in line for label in label_blacklist):
                    company_name = line.strip()

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

            # Extract 名称

        return {
            "发票号码": invoice_number,
            "开票日期": invoice_date,
            "名称": company_name
        }
    pdf_path = "/Users/michaelwu/Downloads/digital_25117000000774505894.pdf"


    result = extract_invoice_data("temp_invoice.pdf")

    st.write("### 📋 Extracted Info:")
    st.json(result)

    if st.button("Save to CSV"):
        df = pd.DataFrame([result])
        df.to_csv("invoices_extracted.csv", mode='a', header=not os.path.exists("/Users/michaelwu/Downloads/invoices_extracted.csv"), index=False)
        st.success("Saved to invoices_extracted.csv ✅")



#Change to Commit
