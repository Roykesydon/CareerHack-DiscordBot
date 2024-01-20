import os
import time

from bson import ObjectId

from core.utils.config import CONFIG
from core.utils.database import mongo_database
from main import chat_bot


class UploadFileManager:
    AVAILABLE_FILE_TYPE_DICT = {
        "text/plain": "txt",
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }

    def get_available_file_list(self, user_id: str):
        file_with_id_list = []

        # get all shared file
        docs = mongo_database["UserUploadFile"].find({"file_scope": "shared"})
        for doc in docs:
            file_with_id_list.append(
                {
                    "file_id": str(doc["_id"]),
                    "file_name": doc["custom_file_name"],
                    "file_scope": doc["file_scope"],
                    "emoji": "🌐",
                }
            )

        # get user's private file
        docs = mongo_database["UserUploadFile"].find(
            {"user_id": user_id, "file_scope": "private"}
        )
        for doc in docs:
            file_with_id_list.append(
                {
                    "file_id": str(doc["_id"]),
                    "file_name": doc["custom_file_name"],
                    "file_scope": doc["file_scope"],
                    "emoji": "🔒",
                }
            )

        return file_with_id_list

    def upload_file(
        self, attachment, custom_file_name: str, attachment_response, user_id: str
    ):
        """
        TODO: check document type, size
        """

        if attachment.content_type is None:
            attachment.content_type = "text/plain"

        file_name = attachment.filename
        insert_data = {
            "file_name": file_name,
            "custom_file_name": custom_file_name
            if custom_file_name != ""
            else file_name,
            "file_type": attachment.content_type,
            "file_url": attachment.url,
            "file_time": int(time.time()),
            "file_scope": "private",
            "user_id": user_id,
            "filename_extension": UploadFileManager.AVAILABLE_FILE_TYPE_DICT[
                attachment.content_type
            ],
        }
        mongo_database["UserUploadFile"].insert_one(insert_data)

        # get document id from mongo as file name
        # save file to local storage
        file = mongo_database["UserUploadFile"].find_one(insert_data)
        if file is not None:
            file_name = str(file["_id"])

        if attachment.content_type is not None:
            with open(
                f"{CONFIG['storage_path']}/{file_name}.{UploadFileManager.AVAILABLE_FILE_TYPE_DICT[attachment.content_type]}",
                "wb",
            ) as file:
                file.write(attachment_response.content)

            file_paths = [
                f"{CONFIG['storage_path']}/{file_name}.{UploadFileManager.AVAILABLE_FILE_TYPE_DICT[attachment.content_type]}"
            ]
            chat_bot.add_documents_to_vector_db(file_paths)

    def delete_file(self, file_id_list: list):
        for file_id in file_id_list:
            # get file extension
            doc = mongo_database["UserUploadFile"].find_one({"_id": ObjectId(file_id)})

            if doc is None:
                continue

            file_name = doc["custom_file_name"]
            extension = doc["filename_extension"]

            mongo_database["UserUploadFile"].delete_one({"_id": ObjectId(file_id)})
            chat_bot.delete_documents_from_vector_db([f"{file_id}.{extension}"])

            # remove file from storage
            os.remove(f"storage/{file_id}.{extension}")

    def toggle_file_scope(self, file_id_list: list):
        for file_id in file_id_list:
            doc = mongo_database["UserUploadFile"].find_one({"_id": ObjectId(file_id)})

            if doc is None:
                continue

            if doc["file_scope"] == "private":
                mongo_database["UserUploadFile"].update_one(
                    {"_id": ObjectId(file_id)}, {"$set": {"file_scope": "shared"}}
                )
            else:
                mongo_database["UserUploadFile"].update_one(
                    {"_id": ObjectId(file_id)}, {"$set": {"file_scope": "private"}}
                )

    def get_file_path(self, file_id: str):
        doc = mongo_database["UserUploadFile"].find_one({"_id": ObjectId(file_id)})
        if doc is None:
            return None

        extension = doc["filename_extension"]

        return f"{CONFIG['storage_path']}/{file_id}.{extension}"
