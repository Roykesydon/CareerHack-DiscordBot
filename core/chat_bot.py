from enum import Enum

import discord
from bson.objectid import ObjectId

from core.utils.config import CONFIG
from core.utils.database import mongo_database
from core.utils.text_manager import TextManager
from VDB_API.hacker_rank_tools import HackerRankTools


class LLMType(Enum):
    GPT3 = "gpt3"
    GPT4 = "gpt4"
    OFFLINE = "offline"


class ChatBot:
    def __init__(self):
        self.TRUNCATE_CONTENT_THRESHOLD = 45

        self._start_chat_channel_set = set()
        self._channel_file_scope_dict = {}

        self._text_manager = TextManager()

        self._MODEL_TYPE = {
            LLMType.GPT3.value: "gpt3",
            LLMType.GPT4.value: "gpt4",
            LLMType.OFFLINE.value: "offline",
        }

        self._ai_engine_api_dict = {}

        self._channel_model_setting_dict = {}

        """
        LLM API
        """
        for key, value in self._MODEL_TYPE.items():
            self._ai_engine_api_dict[key] = HackerRankTools()
            self._ai_engine_api_dict[key].vectordb_manager.set_vector_db(
                CONFIG["vector_db_name"]
            )
            self._ai_engine_api_dict[key].set_llm_type(llm_type=value)

    def _get_default_model_setting_template(self):
        return {
            "model_type": LLMType.GPT3.value,
            "secondary_search": True,
        }

    def chat(self, query, file_scope, channel_id: str, user_id: str):
        ai_engine_api = self._ai_engine_api_dict[self.get_llm_type(channel_id)]
        ai_engine_api.set_secondary_search(
            secondary_search=self._channel_model_setting_dict[channel_id][
                "secondary_search"
            ]
        )

        available_file_list = []
        docs = mongo_database["UserUploadFile"].find({"file_scope": "shared"})
        for doc in docs:
            available_file_list.append(f"{str(doc['_id'])}.{doc['filename_extension']}")
        docs = mongo_database["UserUploadFile"].find(
            {"user_id": user_id, "file_scope": "private"}
        )
        for doc in docs:
            available_file_list.append(f"{str(doc['_id'])}.{doc['filename_extension']}")

        ans, contents, metadatas = ai_engine_api.chat(
            query=query,
            specified_files=file_scope,
            all_accessible_files=available_file_list,
        )
        return ans, contents, metadatas

    def get_show_reference_callback(
        self, channel_id, contents, metadatas, reference_button, view
    ):
        LANG_DATA = self._text_manager.get_selected_language(str(channel_id))

        async def show_reference(interaction):
            color = CONFIG["primary_color"]
            color_int = int(color.replace("#", ""), 16)
            embed = discord.Embed(
                title=LANG_DATA["commands"]["ask"]["reference"][
                    "reference_embed_title"
                ],
                color=color_int,
            )

            collection = mongo_database.get_collection("UserUploadFile")

            if metadatas is not None:
                for index, metadata in enumerate(metadatas):
                    # get custom_file_name
                    custom_file_name = collection.find_one(
                        {"_id": ObjectId(metadata["source"].split(".")[0])}
                    )

                    if custom_file_name is not None:
                        custom_file_name = custom_file_name["custom_file_name"]
                    # with divider
                    if index != 0:
                        embed.add_field(
                            name="\n",
                            value="",
                            inline=True,
                        )
                    if contents is not None:
                        reference_content = contents[index]

                        reference_content = reference_content.replace("\n", " ")

                        # truncate content
                        if len(reference_content) > self.TRUNCATE_CONTENT_THRESHOLD:
                            reference_content = (
                                reference_content[: self.TRUNCATE_CONTENT_THRESHOLD]
                                + "..."
                            )

                        source_info = f"{LANG_DATA['commands']['ask']['reference']['content_prefix']}\
                            {reference_content}\n{LANG_DATA['commands']['ask']['reference']['source_prefix']}\
                                {custom_file_name}\n{LANG_DATA['commands']['ask']['reference']['page_prefix']}\
                                    {metadata['page']+1}"

                        embed.add_field(
                            name=f"{LANG_DATA['commands']['ask']['reference']['field_name']} {index+1}",
                            value=source_info,
                            inline=False,
                        )

                # disable button
                reference_button.disabled = True

                await interaction.response.edit_message(view=view)
                await interaction.followup.send(embed=embed)

        return show_reference

    def set_secondary_search(self, channel_id: str, secondary_search: bool):
        if channel_id not in self._channel_model_setting_dict:
            self._channel_model_setting_dict[
                channel_id
            ] = self._get_default_model_setting_template()

        self._channel_model_setting_dict[channel_id][
            "secondary_search"
        ] = secondary_search

    def get_model_setting(self, channel_id: str):
        if channel_id not in self._channel_model_setting_dict:
            self._channel_model_setting_dict[
                channel_id
            ] = self._get_default_model_setting_template()

        return self._channel_model_setting_dict[channel_id]

    def switch_model(self, channel_id: str, llm_type: LLMType):
        if channel_id not in self._channel_model_setting_dict:
            self._channel_model_setting_dict[
                channel_id
            ] = self._get_default_model_setting_template()

        self._channel_model_setting_dict[channel_id]["model_type"] = llm_type.value

    def get_llm_type(self, channel_id: str):
        if channel_id not in self._channel_model_setting_dict:
            self._channel_model_setting_dict[
                channel_id
            ] = self._get_default_model_setting_template()

        return self._channel_model_setting_dict[channel_id]["model_type"]

    def get_file_list(self, file_id_list: list):
        file_list = []
        db_collection = mongo_database.get_collection("UserUploadFile")

        for file_id in file_id_list:
            file = db_collection.find_one({"_id": ObjectId(file_id)})
            if file is not None:
                file_list.append(file)

        return file_list

    def get_file_name_list(self, file_id_list: list):
        file_list = self.get_file_list(file_id_list)
        file_name_list = [
            f"{str(x['_id'])}.{x['filename_extension']}" for x in file_list
        ]

        return file_name_list

    """
    Dummy setters and getters
    """

    def insert_start_chat_channel(self, channel_id: str):
        self._start_chat_channel_set.add(channel_id)

    def remove_start_chat_channel(self, channel_id: str):
        self._start_chat_channel_set.remove(channel_id)

    def set_channel_file_scope(self, channel_id: str, file_id_list: list):
        file_name_list = self.get_file_name_list(file_id_list)

        self._channel_file_scope_dict[channel_id] = file_name_list

    def get_channel_file_scope(self, channel_id: str):
        return self._channel_file_scope_dict[channel_id]

    def get_start_chat_channel_set(self):
        return self._start_chat_channel_set

    def add_documents_to_vector_db(self, documents):
        self._ai_engine_api_dict["gpt3"].add_documents_to_vdb(documents)

    def delete_documents_from_vector_db(self, documents):
        self._ai_engine_api_dict["gpt3"].delete(documents)
