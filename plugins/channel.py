# ============================================================
# AUTO FILTER LUCY - CHANNEL INDEXER
# ============================================================

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import RPCError

from info import CHANNELS
from database.ia_filterdb import save_file


# ------------------------------------------------------------
# Supported media types
# ------------------------------------------------------------

media_filter = (
    filters.document
    | filters.video
    | filters.audio
)


# ------------------------------------------------------------
# Channel Media Handler
# ------------------------------------------------------------

@Client.on_message(
    filters.chat(CHANNELS) & media_filter
)
async def media(bot, message):

    try:

        # ----------------------------------------------------
        # Find the actual media object
        # ----------------------------------------------------

        media = None
        file_type = None

        for current_type in (
            "document",
            "video",
            "audio"
        ):

            current_media = getattr(
                message,
                current_type,
                None
            )

            if current_media is not None:

                media = current_media
                file_type = current_type
                break

        # ----------------------------------------------------
        # No supported media
        # ----------------------------------------------------

        if media is None:
            return

        # ----------------------------------------------------
        # Attach required information
        # ----------------------------------------------------

        media.file_type = file_type

        media.caption = message.caption or ""

        # ----------------------------------------------------
        # Save to MongoDB index
        # ----------------------------------------------------

        await save_file(
            bot,
            media
        )

        # ----------------------------------------------------
        # Logging
        # ----------------------------------------------------

        file_name = getattr(
            media,
            "file_name",
            None
        )

        if not file_name:

            file_name = (
                getattr(media, "file_name", None)
                or "Unknown File"
            )

        print(
            f"[INDEXED] "
            f"{message.chat.id} | "
            f"{file_name}"
        )

    except RPCError as e:

        print(
            f"[CHANNEL INDEX ERROR] "
            f"{type(e).__name__}: {e}"
        )

    except Exception as e:

        print(
            f"[CHANNEL INDEX ERROR] "
            f"{type(e).__name__}: {e}"
    )
