import re
import os
from PyPDF2 import PdfReader
from docx import Document
import streamlit as st

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

# Hàm chia văn bản thành các chương dựa trên tên chương "Chương I", "Chương II", v.v.
def split_into_chapters(text):
    # Tìm các phần có dấu hiệu bắt đầu chương: "Chương I", "Chương II", ...
    chapters = re.split(r'(Chương\s+[IVXLCDM]+)', text)
    
    # Tạo danh sách các chương và loại bỏ các phần không cần thiết (kể cả phần đầu là rỗng)
    chapters = [chapter.strip() for chapter in chapters if chapter.strip()]
    
    # Nếu chương có thể chứa phần đầu tiên, ta cần ghép lại để hoàn thiện
    chapter_list = []
    for i in range(0, len(chapters), 2):
        if i+1 < len(chapters):
            chapter_list.append(chapters[i] + "\n" + chapters[i+1])
        else:
            chapter_list.append(chapters[i])
    
    return chapter_list

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
                label=f"Tải chương {i}",
                data=f,
                file_name=os.path.basename(file),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # Xoá các file sau khi tải về
    for file in output_files:
        os.remove(file)
