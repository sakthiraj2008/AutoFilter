import logging
from database.config_db import mdb
from info import CHANNELS as ENV_CHANNELS

logger = logging.getLogger(__name__)
COLLECTION = "index_channels"

def _normalise(ch):
    if isinstance(ch, int):
        return ch
    ch = str(ch).strip()
    try:
        return int(ch)
    except ValueError:
        return ch

async def get_index_channels():
    """Return the runtime index-channel list. Seeds MongoDB from CHANNELS once."""
    docs = await mdb.config_col.find({"type": COLLECTION}).sort("chat_id", 1).to_list(length=500)
    if not docs:
        seeds = []
        for ch in ENV_CHANNELS:
            chat_id = _normalise(ch)
            seeds.append({"type": COLLECTION, "chat_id": chat_id})
        if seeds:
            try:
                await mdb.config_col.insert_many(seeds, ordered=False)
            except Exception:
                pass
        return [_normalise(x) for x in ENV_CHANNELS]
    return [doc["chat_id"] for doc in docs if "chat_id" in doc]

async def add_index_channel(chat_id, title=None, username=None):
    chat_id = _normalise(chat_id)
    await mdb.config_col.update_one(
        {"type": COLLECTION, "chat_id": chat_id},
        {"$set": {"type": COLLECTION, "chat_id": chat_id,
                  "title": title, "username": username}},
        upsert=True,
    )
    return chat_id

async def remove_index_channel(chat_id):
    chat_id = _normalise(chat_id)
    result = await mdb.config_col.delete_one({"type": COLLECTION, "chat_id": chat_id})
    return result.deleted_count > 0

async def clear_index_channels():
    result = await mdb.config_col.delete_many({"type": COLLECTION})
    return result.deleted_count
