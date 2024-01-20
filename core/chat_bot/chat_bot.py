import discord
from bson.objectid import ObjectId

from core.utils.config import CONFIG
from core.utils.database import mongo_database
from core.utils.text_manager import TextManager
from VDB_API.hacker_rank_tools import HackerRankTools


class ChatBot:
    def __init__(self):
        self.TRUNCATE_CONTENT_THRESHOLD = 45

        self.start_chat_channel_set = set()
        self.channel_file_scope_dict = {}

        self.text_manager = TextManager()

        self.offline_channel_set = set()

        """
        LLM API
        """
        self.hacker_rank_tools = HackerRankTools()
        self.hacker_rank_tools.vectordb_manager.set_vector_db(CONFIG["vector_db_name"])

        self.hacker_rank_tools_offline = HackerRankTools()
        self.hacker_rank_tools_offline.vectordb_manager.set_vector_db(
            CONFIG["vector_db_name"]
        )

        # 設置線上/線下模型
        self.hacker_rank_tools.set_llm_type(isOnline=True)
        self.hacker_rank_tools_offline.set_llm_type(isOnline=False)

    def chat(self, query, file_scope, channel_id: str):
        if self.is_online(channel_id):
            ans, contents, metadatas = self.hacker_rank_tools.chat(query, file_scope)
        else:
            ans, contents, metadatas = self.hacker_rank_tools_offline.chat(
                query, file_scope
            )
        return ans, contents, metadatas

    def get_show_reference_callback(
        self, channel_id, contents, metadatas, reference_button, view
    ):
        LANG_DATA = self.text_manager.get_selected_language(str(channel_id))

        async def show_reference(interaction):
            color = CONFIG["primary_color"]
            color_int = int(color.replace("#", ""), 16)
            embed = discord.Embed(
                title=LANG_DATA["events"]["directly_chat"]["reference_embed_title"],
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

                        source_info = f"{LANG_DATA['events']['directly_chat']['content_prefix']}\
                            {reference_content}\n{LANG_DATA['events']['directly_chat']['source_prefix']}\
                                {custom_file_name}\n{LANG_DATA['events']['directly_chat']['page_prefix']}\
                                    {metadata['page']+1}"

                        embed.add_field(
                            name=f"{LANG_DATA['events']['directly_chat']['field_name']} {index+1}",
                            value=source_info,
                            inline=False,
                        )

                # disable button
                reference_button.disabled = True

                await interaction.response.edit_message(view=view)
                await interaction.followup.send(embed=embed)

        return show_reference

    def switch_model(self, channel_id: str, online: bool):
        if online:
            self.offline_channel_set.discard(str(channel_id))
        else:
            self.offline_channel_set.add(str(channel_id))

    def is_online(self, channel_id: str):
        return channel_id not in self.offline_channel_set

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
    Setters and getters
    """

    def insert_start_chat_channel(self, channel_id: str):
        self.start_chat_channel_set.add(channel_id)

    def remove_start_chat_channel(self, channel_id: str):
        self.start_chat_channel_set.remove(channel_id)

    def set_channel_file_scope(self, channel_id: str, file_id_list: list):
        file_name_list = self.get_file_name_list(file_id_list)

        self.channel_file_scope_dict[channel_id] = file_name_list

    def get_channel_file_scope(self, channel_id: str):
        return self.channel_file_scope_dict[channel_id]

    def get_start_chat_channel_set(self):
        return self.start_chat_channel_set

    def add_documents_to_vector_db(self, documents):
        self.hacker_rank_tools.add_documents_to_vdb(documents)

    def delete_documents_from_vector_db(self, documents):
        self.hacker_rank_tools.delete(documents)
