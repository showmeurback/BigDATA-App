import docx
import os

def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Читаем все .docx файлы в папке requirements
requirements_dir = 'requirements'
for filename in os.listdir(requirements_dir):
    if filename.endswith('.docx'):
        file_path = os.path.join(requirements_dir, filename)
        print(f"Содержимое файла {filename}:")
        print(read_docx(file_path))
        print("\n" + "="*50 + "\n")