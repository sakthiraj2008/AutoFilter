from pyrogram import Client, filters, enums
from pyrogram.errors import RPCError

from info import ADMINS
from database.index_channels import get_index_channels
from database.ia_filterdb import Media, Media2


@Client.on_message(
    filters.command("indexstatus") &
    filters.private &
    filters.user(ADMINS)
)
async def index_status(bot, message):

    status_msg = None

    try:
        status_msg = await message.reply_text(
            "⏳ <b>Checking index status...</b>",
            parse_mode=enums.ParseMode.HTML
        )

        channels = await get_index_channels()

        if not channels:
            await status_msg.edit_text(
                "📊 <b>INDEX STATUS</b>\n\n"
                "❌ No index channels configured.",
                parse_mode=enums.ParseMode.HTML
            )
            return

        lines = [
            "📊 <b>INDEX STATUS</b>",
            "",
            "━━━━━━━━━━━━━━━━━━"
        ]

        total_files = 0
        accessible = 0
        failed = 0

        # Get bot's own ID
        me = await bot.get_me()
        bot_id = me.id

        for channel_id in channels:

            try:
                # Get channel information
                chat = await bot.get_chat(channel_id)

                # Check bot's access
                member = await bot.get_chat_member(
                    chat.id,
                    bot_id
                )

                member_status = str(member.status)

                if "OWNER" in member_status:
                    access = "Owner"
                    icon = "🟢"

                elif "ADMINISTRATOR" in member_status:
                    access = "Administrator"
                    icon = "🟢"

                elif "MEMBER" in member_status:
                    access = "Member"
                    icon = "🟡"

                else:
                    access = member_status
                    icon = "🔴"

                # Count indexed files
                primary_count = await Media.count_documents({
                    "source_chat_id": chat.id
                })

                secondary_count = await Media2.count_documents({
                    "source_chat_id": chat.id
                })

                indexed_count = primary_count + secondary_count

                total_files += indexed_count
                accessible += 1

                title = (
                    chat.title
                    or chat.first_name
                    or str(chat.id)
                )

                username = (
                    f"@{chat.username}"
                    if chat.username
                    else "Private"
                )

                lines.append(
                    f"{icon} <b>{title}</b>\n"
                    f"🆔 ID: <code>{chat.id}</code>\n"
                    f"👤 {username}\n"
                    f"🔐 Access: <b>{access}</b>\n"
                    f"📁 Indexed Files: <b>{indexed_count}</b>\n"
                )

            except Exception as e:

                failed += 1

                lines.append(
                    "🔴 <b>CHANNEL ERROR</b>\n"
                    f"🆔 ID: <code>{channel_id}</code>\n"
                    f"❌ <code>{type(e).__name__}: "
                    f"{str(e)[:150]}</code>\n"
                )

        lines.extend([
            "━━━━━━━━━━━━━━━━━━",
            f"📡 <b>Total Channels:</b> {len(channels)}",
            f"🟢 <b>Checked:</b> {accessible}",
            f"🔴 <b>Failed:</b> {failed}",
            f"📁 <b>Total Indexed:</b> {total_files}",
            "━━━━━━━━━━━━━━━━━━"
        ])

        await status_msg.edit_text(
            "\n".join(lines),
            parse_mode=enums.ParseMode.HTML
        )

    except RPCError as e:

        error_text = (
            "❌ <b>Telegram Error</b>\n\n"
            f"<code>{type(e).__name__}: {e}</code>"
        )

        if status_msg:
            await status_msg.edit_text(
                error_text,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                error_text,
                parse_mode=enums.ParseMode.HTML
            )

    except Exception as e:

        print(
            f"[INDEX STATUS ERROR] "
            f"{type(e).__name__}: {e}"
        )

        error_text = (
            "❌ <b>Index Status Error</b>\n\n"
            f"<code>{type(e).__name__}: {e}</code>"
        )

        if status_msg:
            await status_msg.edit_text(
                error_text,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                error_text,
                parse_mode=enums.ParseMode.HTML
            )
