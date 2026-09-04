from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus

from info import ADMINS, CHANNELS


@Client.on_message(
    filters.command("indexstatus") & filters.user(ADMINS)
)
async def index_status(bot, message):

    try:

        if not CHANNELS:
            await message.reply_text(
                "📊 <b>INDEX STATUS</b>\n\n"
                "❌ No index channels configured.",
                parse_mode="html"
            )
            return

        text = "📊 <b>INDEX STATUS</b>\n\n"

        accessible = 0
        failed = 0

        for channel in CHANNELS:

            try:

                chat = await bot.get_chat(channel)

                member = await bot.get_chat_member(
                    chat.id,
                    "me"
                )

                title = (
                    chat.title
                    or chat.first_name
                    or str(chat.id)
                )

                status = member.status

                # Correct Pyrogram enum check
                if status == ChatMemberStatus.OWNER:
                    access = "Owner"
                    icon = "🟢"
                    accessible += 1

                elif status == ChatMemberStatus.ADMINISTRATOR:
                    access = "Administrator"
                    icon = "🟢"
                    accessible += 1

                elif status == ChatMemberStatus.MEMBER:
                    access = "Member"
                    icon = "🟢"
                    accessible += 1

                else:
                    access = str(status)
                    icon = "🟡"

                text += (
                    f"{icon} <b>{title}</b>\n"
                    f"🆔 ID: <code>{chat.id}</code>\n"
                    f"🔐 Access: <code>{access}</code>\n\n"
                )

            except Exception as e:

                failed += 1

                text += (
                    f"🔴 <b>Channel Error</b>\n"
                    f"🆔 ID: <code>{channel}</code>\n"
                    f"❌ Error: <code>{type(e).__name__}</code>\n\n"
                )

        text += (
            "━━━━━━━━━━━━━━━━━━\n"
            f"📡 Total Channels: <b>{len(CHANNELS)}</b>\n"
            f"🟢 Accessible: <b>{accessible}</b>\n"
            f"🔴 Failed: <b>{failed}</b>\n"
            "━━━━━━━━━━━━━━━━━━"
        )

        await message.reply_text(
            text,
            parse_mode="html"
        )

    except Exception as e:

        print(
            f"[INDEX STATUS ERROR] "
            f"{type(e).__name__}: {e}"
        )

        await message.reply_text(
            "❌ <b>Index Status Error</b>\n\n"
            f"<code>{type(e).__name__}: {e}</code>",
            parse_mode="html"
        )
