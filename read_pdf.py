import PyPDF2
import sys

def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"عدد الصفحات في الملف: {num_pages}")
            
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
                
        return text
    except Exception as e:
        return f"حدث خطأ أثناء قراءة الملف: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        text = extract_text_from_pdf(pdf_path)
        print(text[:1000])  
        
        with open('extracted_pdf_text.txt', 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        print("تم حفظ النص المستخرج في ملف 'extracted_pdf_text.txt'")
    else:
        print("الرجاء تحديد مسار ملف PDF")
