import re
import logging
from pyrogram import Client, filters, enums
from pyrogram.errors import RPCError
from info import ADMINS
from database.index_channels import (
    get_index_channels, add_index_channel, remove_index_channel, clear_index_channels
)

logger = logging.getLogger(__name__)

def _parse_target(text):
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    value = parts[1].strip()
    if value.startswith("https://t.me/"):
        value = value.rstrip("/").split("/")[-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value

async def _is_admin(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        )
    except Exception:
        return False

@Client.on_message(filters.command("addindex") & filters.user(ADMINS) & filters.private)
async def addindex(bot, message):
    target = _parse_target(message.text)
    if target is None:
        return await message.reply(
            "<b>Usage:</b> <code>/addindex -1001234567890</code>\n"
            "or <code>/addindex @channelusername</code>"
        )
    try:
        chat = await bot.get_chat(target)
        if chat.type not in (enums.ChatType.CHANNEL, enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            return await message.reply("❌ Please give a Telegram channel/group.")
        if not await _is_admin(bot, chat.id, bot.me.id):
            return await message.reply("❌ I must be an admin in that channel/group to auto-index it.")
        await add_index_channel(chat.id, chat.title, chat.username)
        name = f"@{chat.username}" if chat.username else (chat.title or str(chat.id))
        return await message.reply(
            f"✅ <b>Index channel added.</b>\n\n"
            f"📌 {name}\n🆔 <code>{chat.id}</code>\n\n"
            f"New files posted there will now be indexed automatically."
        )
    except RPCError as e:
        return await message.reply(f"❌ Telegram error: <code>{e}</code>")
    except Exception as e:
        logger.exception(e)
        return await message.reply(f"❌ Error: <code>{e}</code>")

@Client.on_message(filters.command("delindex") & filters.user(ADMINS) & filters.private)
async def delindex(bot, message):
    target = _parse_target(message.text)
    if target is None:
        return await message.reply("<b>Usage:</b> <code>/delindex -1001234567890</code>")
    try:
        chat = await bot.get_chat(target)
        removed = await remove_index_channel(chat.id)
        if removed:
            return await message.reply(f"🗑️ Removed <code>{chat.id}</code> from auto-index channels.")
        return await message.reply("ℹ️ That channel is not in the runtime index list.")
    except Exception as e:
        return await message.reply(f"❌ Error: <code>{e}</code>")

@Client.on_message(filters.command("indexlist") & filters.user(ADMINS) & filters.private)
async def indexlist(bot, message):
    channels = await get_index_channels()
    if not channels:
        return await message.reply("📭 No index channels configured.")
    lines = ["📚 <b>Runtime Index Channels</b>\n"]
    for i, chat_id in enumerate(channels, 1):
        try:
            chat = await bot.get_chat(chat_id)
            name = f"@{chat.username}" if chat.username else (chat.title or "Unknown")
            lines.append(f"{i}. {name}\n   🆔 <code>{chat.id}</code>")
        except Exception:
            lines.append(f"{i}. ⚠️ Unavailable\n   🆔 <code>{chat_id}</code>")
    lines.append(f"\n<b>Total:</b> {len(channels)}")
    text = "\n".join(lines)
    if len(text) <= 4096:
        return await message.reply(text)
    with open("index_channels.txt", "w", encoding="utf8") as f:
        f.write(text)
    try:
        await message.reply_document("index_channels.txt")
    finally:
        import os
        os.remove("index_channels.txt")

@Client.on_message(filters.command("clearindex") & filters.user(ADMINS) & filters.private)
async def clearindex(bot, message):
    count = await clear_index_channels()
    await message.reply(
        f"🗑️ Removed <b>{count}</b> runtime index channel(s).\n"
        "⚠️ Your original CHANNELS env value is not changed. A restart will seed it again."
    )

@Client.on_message(filters.command("indexhelp") & filters.user(ADMINS) & filters.private)
async def indexhelp(bot, message):
    await message.reply(
        "<b>📚 Index Manager</b>\n\n"
        "<code>/addindex -1001234567890</code> — add channel/group\n"
        "<code>/delindex -1001234567890</code> — remove one\n"
        "<code>/indexlist</code> — show all runtime index channels\n"
        "<code>/clearindex</code> — remove runtime additions\n\n"
        "The bot must be an admin in every index channel."
    )
