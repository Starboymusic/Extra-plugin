from inspect import getfullargspec
from re import findall
import datetime

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BANNED_USERS
from ChampuMusic import app
from ChampuMusic.utils.database import (
    delete_note,
    deleteall_notes,
    get_note,
    get_note_names,
    save_note,
)
from utils.error import capture_err
from ChampuMusic.utils.functions import (
    check_format,
    extract_text_and_keyb,
    get_data_and_name,
)
from ChampuMusic.utils.keyboard import ikb
from utils.permissions import adminsOnly, member_permissions


def extract_urls(reply_markup):
    urls = []
    if reply_markup.inline_keyboard:
        buttons = reply_markup.inline_keyboard
        for i, row in enumerate(buttons):
            for j, button in enumerate(row):
                if button.url:
                    name = (
                        "\n~\nbutton"
                        if i * len(row) + j + 1 == 1
                        else f"button{i * len(row) + j + 1}"
                    )
                    urls.append((f"{name}", button.text, button.url))
    return urls


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(filters.command("save") & filters.group & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def save_notee(_, message):
    try:
        if len(message.command) < 2:
            await eor(
                message,
                text="**ᴜsᴀɢᴇ:**\nʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ /save [NOTE_NAME] ᴛᴏ sᴀᴠᴇ ᴀ ɴᴇᴡ ɴᴏᴛᴇ.",
            )
        else:
            replied_message = message.reply_to_message
            if not replied_message:
                replied_message = message
            data, name = await get_data_and_name(replied_message, message)
            if data == "error":
                return await message.reply_text(
                    "**ᴜsᴀɢᴇ:**\n__/save [NOTE_NAME] [CONTENT]__\n`-----------OR-----------`\nʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ.\n/save [NOTE_NAME]"
                )
            if replied_message.text:
                _type = "text"
                file_id = None
            if replied_message.sticker:
                _type = "sticker"
                file_id = replied_message.sticker.file_id
            if replied_message.animation:
                _type = "animation"
                file_id = replied_message.animation.file_id
            if replied_message.photo:
                _type = "photo"
                file_id = replied_message.photo.file_id
            if replied_message.document:
                _type = "document"
                file_id = replied_message.document.file_id
            if replied_message.video:
                _type = "video"
                file_id = replied_message.video.file_id
            if replied_message.video_note:
                _type = "video_note"
                file_id = replied_message.video_note.file_id
            if replied_message.audio:
                _type = "audio"
                file_id = replied_message.audio.file_id
            if replied_message.voice:
                _type = "voice"
                file_id = replied_message.voice.file_id
            if replied_message.reply_markup and not findall(r"\[.+\,.+\]", data):
                urls = extract_urls(replied_message.reply_markup)
                if urls:
                    response = "\n".join(
                        [f"{name}=[{text}, {url}]" for name, text, url in urls]
                    )
                    data = data + response
            if data:
                data = await check_format(ikb, data)
                if not data:
                    return await message.reply_text(
                        "**ᴡʀᴏɴɢ ғᴏʀᴍᴀᴛᴛɪɴɢ, ᴄʜᴇᴄᴋ ᴛʜᴇ ʜᴇʟᴘ sᴇᴄᴛɪᴏɴ.**"
                    )
            note = {
                "type": _type,
                "data": data,
                "file_id": file_id,
            }
            chat_id = message.chat.id
            await save_note(chat_id, name, note)
            await eor(message, text=f"__**sᴀᴠᴇᴅ ɴᴏᴛᴇ {name}.**__")
    except UnboundLocalError:
        return await message.reply_text(
            "**ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪs ɪɴᴀᴄᴄᴇssɪʙʟᴇ.\n`ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ`**"
        )


@app.on_message(filters.command("notes") & filters.group & ~BANNED_USERS)
@capture_err
async def get_notes(_, message):
    chat_id = message.chat.id

    _notes = await get_note_names(chat_id)

    if not _notes:
        return await eor(message, text="**ɴᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
    _notes.sort()
    msg = f"ʟɪsᴛ ᴏғ ɴᴏᴛᴇs ɪɴ {message.chat.title}\n"
    for note in _notes:
        msg += f"**-** `{note}`\n"
    await eor(message, text=msg)


@app.on_message(filters.command("get") & filters.group & ~BANNED_USERS)
@capture_err
async def get_one_note(_, message):
    if len(message.text.split()) < 2:
        return await eor(message, text="ɪɴᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛs")
    from_user = message.from_user if message.from_user else message.sender_chat
    chat_id = message.chat.id
    name = message.text.split(None, 1)[1]
    if not name:
        return
    _note = await get_note(chat_id, name)
    if not _note:
        return
    type = _note["type"]
    data = _note["data"]
    file_id = _note.get("file_id")
    keyb = None
    if data:
        if "{app.mention}" in data:
            data = data.replace("{app.mention}", app.mention)
        if "{GROUPNAME}" in data:
            data = data.replace("{GROUPNAME}", message.chat.title)
        if "{NAME}" in data:
            data = data.replace("{NAME}", message.from_user.mention)
        if "{ID}" in data:
            data = data.replace("{ID}", f"`message.from_user.id`")
        if "{FIRSTNAME}" in data:
            data = data.replace("{FIRSTNAME}", message.from_user.first_name)
        if "{SURNAME}" in data:
            sname = (
                message.from_user.last_name
                if message.from_user.last_name.last_name
                else "None"
            )
            data = data.replace("{SURNAME}", sname)
        if "{USERNAME}" in data:
            susername = (
                message.from_user.username if message.from_user.username else "None"
            )
            data = data.replace("{USERNAME}", susername)
        if "{DATE}" in data:
            DATE = datetime.datetime.now().strftime("%Y-%m-%d")
            data = data.replace("{DATE}", DATE)
        if "{WEEKDAY}" in data:
            WEEKDAY = datetime.datetime.now().strftime("%A")
            data = data.replace("{WEEKDAY}", WEEKDAY)
        if "{TIME}" in data:
            TIME = datetime.datetime.now().strftime("%H:%M:%S")
            data = data.replace("{TIME}", f"{TIME} UTC")

        if findall(r"\[.+\,.+\]", data):
            keyboard = extract_text_and_keyb(ikb, data)
            if keyboard:
                data, keyb = keyboard
    replied_message = message.reply_to_message
    if replied_message:
        replied_user = (
            replied_message.from_user
            if replied_message.from_user
            else replied_message.sender_chat
        )
        if replied_user.id != from_user.id:
            message = replied_message
    await get_reply(message, type, file_id, data, keyb)


@app.on_message(filters.regex(r"^#.+") & filters.text & filters.group & ~BANNED_USERS)
@capture_err
async def get_one_note(_, message):
    from_user = message.from_user if message.from_user else message.sender_chat
    chat_id = message.chat.id
    name = message.text.replace("#", "", 1)
    if not name:
        return
    _note = await get_note(chat_id, name)
    if not _note:
        return
    type = _note["type"]
    data = _note["data"]
    file_id = _note.get("file_id")
    keyb = None
    if data:
        if "{app.mention}" in data:
            data = data.replace("{app.mention}", app.mention)
        if "{GROUPNAME}" in data:
            data = data.replace("{GROUPNAME}", message.chat.title)
        if "{NAME}" in data:
            data = data.replace("{NAME}", message.from_user.mention)
        if "{ID}" in data:
            data = data.replace("{ID}", f"`message.from_user.id`")
        if "{FIRSTNAME}" in data:
            data = data.replace("{FIRSTNAME}", message.from_user.first_name)
        if "{SURNAME}" in data:
            sname = (
                message.from_user.last_name
                if message.from_user.last_name.last_name
                else "None"
            )
            data = data.replace("{SURNAME}", sname)
        if "{USERNAME}" in data:
            susername = (
                message.from_user.username if message.from_user.username else "None"
            )
            data = data.replace("{USERNAME}", susername)
        if "{DATE}" in data:
            DATE = datetime.datetime.now().strftime("%Y-%m-%d")
            data = data.replace("{DATE}", DATE)
        if "{WEEKDAY}" in data:
            WEEKDAY = datetime.datetime.now().strftime("%A")
            data = data.replace("{WEEKDAY}", WEEKDAY)
        if "{TIME}" in data:
            TIME = datetime.datetime.now().strftime("%H:%M:%S")
            data = data.replace("{TIME}", f"{TIME} UTC")

        if findall(r"\[.+\,.+\]", data):
            keyboard = extract_text_and_keyb(ikb, data)
            if keyboard:
                data, keyb = keyboard
    replied_message = message.reply_to_message
    if replied_message:
        replied_user = (
            replied_message.from_user
            if replied_message.from_user
            else replied_message.sender_chat
        )
        if replied_user.id != from_user.id:
            message = replied_message
    await get_reply(message, type, file_id, data, keyb)


async def get_reply(message, type, file_id, data, keyb):
    if type == "text":
        await message.reply_text(
            text=data,
            reply_markup=keyb,
            disable_web_page_preview=True,
        )
    if type == "sticker":
        await message.reply_sticker(
            sticker=file_id,
        )
    if type == "animation":
        await message.reply_animation(
            animation=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type == "photo":
        await message.reply_photo(
            photo=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type == "document":
        await message.reply_document(
            document=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type == "video":
        await message.reply_video(
            video=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type == "video_note":
        await message.reply_video_note(
            video_note=file_id,
        )
    if type == "audio":
        await message.reply_audio(
            audio=file_id,
            caption=data,
            reply_markup=keyb,
        )
    if type == "voice":
        await message.reply_voice(
            voice=file_id,
            caption=data,
            reply_markup=keyb,
        )


@app.on_message(filters.command("delete") & filters.group & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def del_note(_, message):
    if len(message.command) < 2:
        return await eor(message, text="**ᴜsᴀɢᴇ**\n__/delete [NOTE_NAME]__")
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await eor(message, text="**ᴜsᴀɢᴇ**\n__/delete [NOTE_NAME]__")

    chat_id = message.chat.id

    deleted = await delete_note(chat_id, name)
    if deleted:
        await eor(message, text=f"**ᴅᴇʟᴇᴛᴇᴅ ɴᴏᴛᴇ {name} sᴜᴄᴄᴇssғᴜʟʟʏ.**")
    else:
        await eor(message, text="**ɴᴏ sᴜᴄʜ ɴᴏᴛᴇ.**")


@app.on_message(filters.command("deleteall") & filters.group & ~BANNED_USERS)
@adminsOnly("can_change_info")
async def delete_all(_, message):
    _notes = await get_note_names(message.chat.id)
    if not _notes:
        return await message.reply_text("**ɴᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("ʏᴇs, ᴅᴏ ɪᴛ", callback_data="delete_yes"),
                    InlineKeyboardButton("ᴄᴀɴᴄᴇʟ", callback_data="delete_no"),
                ]
            ]
        )
        await message.reply_text(
            "**ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴛʜᴇ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ ғᴏʀᴇᴠᴇʀ ?.**",
            reply_markup=keyboard,
        )


@app.on_callback_query(filters.regex("delete_(.*)"))
async def delete_all_cb(_, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_change_info"
    if permission not in permissions:
        return await cb.answer(
            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴘᴇʀᴍɪssɪᴏɴ.\n ᴘᴇʀᴍɪssɪᴏɴ: {permission}",
            show_alert=True,
        )
    input = cb.data.split("_", 1)[1]
    if input == "yes":
        stoped_all = await deleteall_notes(chat_id)
        if stoped_all:
            return await cb.message.edit(
                "**sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴀʟʟ ɴᴏᴛᴇs ᴏɴ ᴛʜɪs ᴄʜᴀᴛ.**"
            )
    if input == "no":
        await cb.message.reply_to_message.delete()
        await cb.message.delete()


__MODULE__ = "Nᴏᴛᴇs"
__HELP__ = """
**ɴᴏᴛᴇꜱ:**

• `/save [NOTE_NAME] [CONTENT]`: Sᴀᴠᴇs ᴀ ɴᴏᴛᴇ ᴡɪᴛʜ ᴛʜᴇ ɢɪᴠᴇɴ ɴᴀᴍᴇ ᴀɴᴅ ᴄᴏɴᴛᴇɴᴛ.
• `/notes`: Sʜᴏᴡs ᴀʟʟ sᴀᴠᴇᴅ ɴᴏᴛᴇꜱ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ.
• `/get [NOTE_NAME]`: Gᴇᴛs ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ ᴏғ ᴀ sᴀᴠᴇᴅ ɴᴏᴛᴇ.
• `/delete [NOTE_NAME]`: Dᴇʟᴇᴛᴇs ᴀ sᴀᴠᴇᴅ ɴᴏᴛᴇ.
• `/deleteall`: Dᴇʟᴇᴛᴇs ᴀʟʟ sᴀᴠᴇᴅ ɴᴏᴛᴇꜱ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ.
"""
