from pyrogram import Client, filters
from info import ADMINS, CHANNELS


@Client.on_message(filters.command("indexstatus") & filters.private)
async def index_status(bot, message):
    try:
        # Admin only
        if message.from_user.id not in ADMINS:
            return await message.reply_text(
                "❌ You are not authorized to use this command."
            )

        if not CHANNELS:
            return await message.reply_text(
                "📂 <b>Index Status</b>\n\n"
                "❌ No index channels configured."
            )

        text = "📊 <b>INDEX STATUS</b>\n\n"

        working = 0
        failed = 0

        for channel in CHANNELS:
            try:
                chat = await bot.get_chat(channel)

                # Check bot's access
                try:
                    member = await bot.get_chat_member(
                        chat.id,
                        "me"
                    )

                    status = str(member.status)

                    if status in ["administrator", "owner"]:
                        icon = "🟢"
                        working += 1
                        access = "Admin"
                    elif status == "member":
                        icon = "🟢"
                        working += 1
                        access = "Member"
                    else:
                        icon = "🟡"
                        access = status

                except Exception:
                    icon = "🟡"
                    access = "Unknown"

                title = chat.title or chat.first_name or str(chat.id)

                text += (
                    f"{icon} <b>{title}</b>\n"
                    f"   ID: <code>{chat.id}</code>\n"
                    f"   Access: <code>{access}</code>\n\n"
                )

            except Exception as e:
                failed += 1

                text += (
                    f"🔴 <b>Channel Error</b>\n"
                    f"   ID: <code>{channel}</code>\n"
                    f"   Error: <code>{type(e).__name__}</code>\n\n"
                )

        text += (
            "━━━━━━━━━━━━━━━━━━\n"
            f"📡 Total Channels: <b>{len(CHANNELS)}</b>\n"
            f"🟢 Accessible: <b>{working}</b>\n"
            f"🔴 Failed: <b>{failed}</b>\n"
            "━━━━━━━━━━━━━━━━━━"
        )

        await message.reply_text(text)

    except Exception as e:
        print(f"[INDEX STATUS ERROR] {e}")

        await message.reply_text(
            f"❌ <b>Index Status Error</b>\n\n"
            f"<code>{type(e).__name__}: {e}</code>"
        )
