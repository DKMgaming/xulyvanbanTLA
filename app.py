import re
import os
from PyPDF2 import PdfReader
from docx import Document
import streamlit as st
from io import BytesIO

# Hàm trích xuất văn bản từ file PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = []
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text.append(page.extract_text())
    return ''.join(text)

# Làm sạch văn bản cho Word
def clean_text_for_word(text):
    cleaned_text = re.sub(r'[\x00-\x1F\x7F]', '', text)  # Remove non-printable characters
    cleaned_text = cleaned_text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
    return cleaned_text

# Hàm chia văn bản thành các chương
def split_into_chapters(text):
    chapters = []
    parts = re.split(r'CHƯƠNG\s+\w+', text)
    for part in parts[1:]:
        chapters.append(part.strip())
    return chapters

# Hàm lưu các chương vào file Word
def save_chapters_as_word(chapters):
    output_files = []
    for i, chapter in enumerate(chapters):
        doc = Document()
        doc.add_paragraph(chapter)
        output_path = f"chapter_{i+1}.docx"
        doc.save(output_path)
        output_files.append(output_path)
    return output_files

# Hàm chính để xử lý PDF
def process_pdf(pdf_file):
    text = extract_text_from_pdf(pdf_file)
    cleaned_text = clean_text_for_word(text)
    chapters = split_into_chapters(cleaned_text)
    output_files = save_chapters_as_word(chapters)
    return output_files

# Streamlit UI
st.title("Chia PDF thành các chương và tải về")
st.markdown("Tải lên file PDF và hệ thống sẽ xử lý để chia thành các chương và xuất thành các file Word.")

# Tải lên file PDF
uploaded_file = st.file_uploader("Chọn file PDF", type=["pdf"])

if uploaded_file is not None:
    # Hiển thị file đã tải lên
    st.write("Đang xử lý file:", uploaded_file.name)

    # Xử lý PDF và lưu các chương thành các file Word
    output_files = process_pdf(uploaded_file)

    # Tạo liên kết để tải các file về
    st.markdown("### Các chương đã được tạo. Tải về các file Word dưới đây:")
    for i, file in enumerate(output_files):
        with open(file, "rb") as f:
            st.download_button(
                label=f"Tải chương {i+1}",
                data=f,
                file_name=os.path.basename(file),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # Xoá các file sau khi tải về
    for file in output_files:
        os.remove(file)
