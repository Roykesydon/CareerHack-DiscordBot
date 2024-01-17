from bson import ObjectId

from core.database import mongo_database


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

    def delete_file(self, file_id: str):
        mongo_database["UserUploadFile"].delete_one({"_id": ObjectId(file_id)})
