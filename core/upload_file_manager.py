import os

from bson import ObjectId

from core.config import CONFIG
from core.database import mongo_database
from main import hacker_rank_tools


class UploadFileManager:
    def get_available_file_list(self, user_id: str):
        file_with_id_list = []

        # get all shared file
        docs = mongo_database["UserUploadFile"].find({"file_scope": "shared"})
        for doc in docs:
            file_with_id_list.append(
                {"file_id": str(doc["_id"]), "file_name": doc["custom_file_name"]}
            )

        # get user's private file
        docs = mongo_database["UserUploadFile"].find(
            {"user_id": user_id, "file_scope": "private"}
        )
        for doc in docs:
            file_with_id_list.append(
                {"file_id": str(doc["_id"]), "file_name": doc["custom_file_name"]}
            )

        return file_with_id_list

    def delete_file(self, file_id_list: list):
        for file_id in file_id_list:
            # get file extension
            doc = mongo_database["UserUploadFile"].find_one({"_id": ObjectId(file_id)})
            file_name = doc["custom_file_name"]
            extension = doc["filename_extension"]

            mongo_database["UserUploadFile"].delete_one({"_id": ObjectId(file_id)})
            hacker_rank_tools.delete([f"{file_id}.{extension}"])

            # remove file from storage
            os.remove(f"storage/{file_id}.{extension}")

    def get_file_path(self, file_id: str):
        doc = mongo_database["UserUploadFile"].find_one({"_id": ObjectId(file_id)})
        extension = doc["filename_extension"]

        return f"{CONFIG['storage_path']}/{file_id}.{extension}"
