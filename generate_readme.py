import zipfile
import xml.etree.ElementTree as ET
import sys
import re
import os

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            texts = []
            for para in tree.findall('.//w:p', ns):
                para_text = ''
                for run in para.findall('.//w:r', ns):
                    for child in run:
                        if child.tag == f"{{{ns['w']}}}t" and child.text:
                            para_text += child.text
                        elif child.tag == f"{{{ns['w']}}}tab":
                            para_text += '\t'
                if para_text.strip():
                    texts.append(para_text.strip())
            return '\n'.join(texts)
    except Exception as e:
        return str(e)

def main():
    base_dir = r"D:\个人\04赚钱项目\02数据常青藤\blog_v2\docs\书籍git仓库\[书籍]python数据分析与数据化运营 - 第1版"
    wuliao_dir = os.path.join(base_dir, "README物料")
    book_title = "[书籍]python数据分析与数据化运营 - 第1版"

    # 1. Rename image
    image_ext = ""
    for f in os.listdir(wuliao_dir):
        if f.endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('[书籍]'):
            image_ext = os.path.splitext(f)[1]
            old_img_path = os.path.join(wuliao_dir, f)
            new_img_name = f"{book_title}{image_ext}"
            new_img_path = os.path.join(wuliao_dir, new_img_name)
            os.rename(old_img_path, new_img_path)
            break
        elif f.startswith('[书籍]') and f.endswith(('.png', '.jpg', '.jpeg')):
            image_ext = os.path.splitext(f)[1]
            break
            
    # 2. Extract Preface
    preface_path = os.path.join(wuliao_dir, "前言.docx")
    preface_text = extract_text_from_docx(preface_path)

    # 3. Extract and clean TOC
    toc_path = os.path.join(wuliao_dir, "目录.docx")
    toc_raw = extract_text_from_docx(toc_path)
    cleaned_toc = []
    for line in toc_raw.split('\n'):
        line = line.strip()
        # Remove trailing tabs/page numbers commonly found in word TOC
        if '\t' in line:
            line = line.rsplit('\t', 1)[0].strip()
        # Ensure it's a chapter/section heading
        if re.match(r'^(第[0-9一二三四五六七八九十百]+章|[0-9]+(\.[0-9]+)*)\s*(.*)', line):
            line = re.sub(r'\s+[0-9]+$', '', line)
            cleaned_toc.append(line)

    # 4. Generate README.md
    readme_content = f"""![封皮](README物料/{book_title}{image_ext})

# {book_title}

## 📖 前言与简介
{preface_text}

## 📑 目录
{chr(10).join(cleaned_toc)}

## 💻 配套资源与附件
- **随书附件**: 本仓库 `随书附件/` 目录下包含了书中所涉及的所有代码、数据文件和配图。
- **联系与勘误**: 如果您在学习过程中发现任何问题或需要交流，欢迎提交 Issue。
"""
    readme_path = os.path.join(base_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("Success")

if __name__ == '__main__':
    main()
