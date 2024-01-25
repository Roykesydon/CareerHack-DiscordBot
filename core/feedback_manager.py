import datetime

from core.utils.database import mongo_database
from core.utils.text_manager import TextManager


class FeedbackManager:
    def __init__(self):
        self._text_manager = TextManager()

    def get_feedback_collection(self):
        return mongo_database.get_collection("Feedback")

    def insert_feedback(self, type, channel_id, query, answer, contents, metadatas):
        feedback_collection = self.get_feedback_collection()
        feedback_collection.insert_one(
            {
                "type": type,
                "channel_id": str(channel_id),
                "query": query,
                "answer": answer,
                "contents": contents,
                "metadatas": metadatas,
                "timestamp": f"{datetime.datetime.now()}",
            }
        )

    def get_good_response_callback(
        self,
        channel_id,
        good_response_button,
        bad_response_button,
        view,
        query,
        answer,
        contents,
        metadatas,
    ):
        LANG_DATA = self._text_manager.get_selected_language(str(channel_id))

        async def response_callback(interaction):
            self.insert_feedback(
                type="good",
                channel_id=channel_id,
                query=query,
                answer=answer,
                contents=contents,
                metadatas=metadatas,
            )

            # disable button
            good_response_button.disabled = True
            bad_response_button.disabled = True

            await interaction.response.edit_message(view=view)
            await interaction.followup.send(
                LANG_DATA["commands"]["ask"]["feedback"]["good_response"]
            )

        return response_callback

    def get_bad_response_callback(
        self,
        channel_id,
        good_response_button,
        bad_response_button,
        view,
        query,
        answer,
        contents,
        metadatas,
    ):
        LANG_DATA = self._text_manager.get_selected_language(str(channel_id))

        async def response_callback(interaction):
            self.insert_feedback(
                type="bad",
                channel_id=channel_id,
                query=query,
                answer=answer,
                contents=contents,
                metadatas=metadatas,
            )

            # disable button
            good_response_button.disabled = True
            bad_response_button.disabled = True

            await interaction.response.edit_message(view=view)
            await interaction.followup.send(
                LANG_DATA["commands"]["ask"]["feedback"]["bad_response"]
            )

        return response_callback
