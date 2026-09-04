from pyrogram import Client, filters, enums
from info import ADMINS
from database.index_channels import get_index_channels
from database.ia_filterdb import Media, Media2


@Client.on_message(filters.command("indexstatus") & filters.private)
async def index_status(bot, message):

    # Admin check
    if not message.from_user or message.from_user.id not in ADMINS:
        return await message.reply_text(
            "❌ <b>Access Denied</b>\n\n"
            "Only bot administrators can use this command.",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        msg = await message.reply_text(
            "⏳ <b>Checking index status...</b>",
            parse_mode=enums.ParseMode.HTML
        )

        channels = await get_index_channels()

        if not channels:
            return await msg.edit_text(
                "📊 <b>INDEX STATUS</b>\n\n"
                "❌ No index channels configured.",
                parse_mode=enums.ParseMode.HTML
            )

        lines = [
            "📊 <b>INDEX STATUS</b>",
            "",
            "━━━━━━━━━━━━━━━━━━"
        ]

        accessible = 0
        failed = 0
        total_files = 0

        for channel_id in channels:

            try:
                chat = await bot.get_chat(channel_id)

                # Check bot access
                try:
                    member = await bot.get_chat_member(
                        chat.id,
                        bot.me.id
                    )
                    bot_status = str(member.status)
                except Exception:
                    bot_status = "Unknown"

                # Count files indexed from this channel
                count1 = await Media.count_documents({
                    "source_chat_id": chat.id
                })

                count2 = await Media2.count_documents({
                    "source_chat_id": chat.id
                })

                count = count1 + count2
                total_files += count

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

                accessible += 1

                lines.append(
                    f"🟢 <b>{title}</b>\n"
                    f"🆔 <code>{chat.id}</code>\n"
                    f"👤 {username}\n"
                    f"🔐 <b>Bot:</b> <code>{bot_status}</code>\n"
                    f"📁 <b>Indexed:</b> {count}\n"
                )

            except Exception as e:

                failed += 1

                lines.append(
                    f"🔴 <b>Channel Error</b>\n"
                    f"🆔 <code>{channel_id}</code>\n"
                    f"❌ <code>{type(e).__name__}</code>\n"
                )

        lines.extend([
            "━━━━━━━━━━━━━━━━━━",
            f"📡 <b>Total Channels:</b> {len(channels)}",
            f"🟢 <b>Accessible:</b> {accessible}",
            f"🔴 <b>Failed:</b> {failed}",
            f"📁 <b>Total Indexed:</b> {total_files}",
            "━━━━━━━━━━━━━━━━━━"
        ])

        await msg.edit_text(
            "\n".join(lines),
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:

        print(
            f"[INDEX STATUS ERROR] "
            f"{type(e).__name__}: {e}"
        )

        try:
            await message.reply_text(
                "❌ <b>Index Status Error</b>\n\n"
                f"<code>{type(e).__name__}: {e}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass
