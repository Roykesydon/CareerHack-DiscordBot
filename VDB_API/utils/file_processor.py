import os
from typing import List

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (Docx2txtLoader, JSONLoader,
                                                  PyPDFLoader, TextLoader)
from langchain_community.document_loaders.csv_loader import CSVLoader

EN_CHUNK_SIZE = 1000
EN_CHUNK_OVERLAP = 400
ZH_CHUNK_SIZE = 400
ZH_CHUNK_OVERLAP = 200

# 根據檔案前面的 2000 長度的字串，檢驗是否含有中文字符
def _is_contains_chinese(str, size=2000):
    sample_str = str[:size]
    for _char in sample_str:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

def _get_loader(file_type, file_path):
    if file_type == ".pdf":
        return PyPDFLoader(file_path)
    elif file_type == ".txt" or file_type == ".md":
        return TextLoader(file_path, encoding="UTF-8")
    # elif file_type == ".json":
    #     return JSONLoader(file_path)
    # elif file_type == ".csv":
    #     return CSVLoader(file_path)
    # elif file_type == ".docx" or file_type == ".doc":
    #     return Docx2txtLoader(file_path)
    else:
        print("file type not supported")
        return None


def get_split_data(file_path) -> List[Document]:
    file_name = os.path.basename(file_path)
    _, file_extension = os.path.splitext(file_path)
    loader = _get_loader(file_extension, file_path)

    if loader is not None:
        doc = loader.load()
        if _is_contains_chinese(doc[0].page_content):
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=ZH_CHUNK_SIZE, chunk_overlap=ZH_CHUNK_OVERLAP, length_function=len
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=EN_CHUNK_SIZE, chunk_overlap=EN_CHUNK_OVERLAP, length_function=len
            )
        texts = splitter.split_documents(doc)

        for text in texts:  # 修改 metadata 的 source 成檔名
            text.metadata["source"] = file_name
        return texts
    else:
        raise Exception("file type not supported")
