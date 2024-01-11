import os
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    JSONLoader,
    Docx2txtLoader,
)
from langchain_community.document_loaders.csv_loader import CSVLoader

CHUNK_SIZE = 100
CHUNK_OVERLAP = 20


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


def get_split_data(file_path) -> list[Document]:
    file_name = os.path.basename(file_path)
    _, file_extension = os.path.splitext(file_path)
    loader = _get_loader(file_extension, file_path)
    if loader is not None:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, length_function=len
        )
        texts = loader.load_and_split(splitter)

        for text in texts:  # 修改 metadata 的 source 成檔名
            text.metadata["source"] = file_name
        return texts
    else:
        raise Exception("file type not supported")
