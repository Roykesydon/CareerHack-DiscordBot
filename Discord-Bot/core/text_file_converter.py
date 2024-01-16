from enum import Enum

import PyPDF2


class FileTypes(Enum):
    TXT = 1
    PDF = 2


class TextFileConverter:
    def get_text_from_file(self, file_path: str, file_type: FileTypes):
        if file_type == FileTypes.TXT:
            with open(file_path, "r", encoding="utf8") as f:
                return f.read()

        elif file_type == FileTypes.PDF:
            text = ""

            pdf_file_obj = open(file_path, "rb")
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            for page_index in range(len(pdf_reader.pages)):
                page_obj = pdf_reader.pages[page_index]
                text += page_obj.extract_text()

            pdf_file_obj.close()
            return text

        else:
            raise ValueError("Invalid file type")
