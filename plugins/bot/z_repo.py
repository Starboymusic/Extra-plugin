import asyncio

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ChampuMusic import app
from ChampuMusic.utils.database import add_served_chat, get_assistant


start_txt = """**
✪ 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗦𝘁𝗮𝗿𝗯𝗼𝘆 𝗥𝗲𝗽𝗼𝘀 ✪

➲ ᴇᴀsʏ ʜᴇʀᴏᴋᴜ ᴅᴇᴘʟᴏʏᴍᴇɴᴛ ✰  
➲ ɴᴏ ʙᴀɴ ɪssᴜᴇs ✰  
➲ ᴜɴʟɪᴍɪᴛᴇᴅ ᴅʏɴᴏs ✰  
➲ 𝟸𝟺/𝟽 ʟᴀɢ-ғʀᴇᴇ ✰

► sᴇɴᴅ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ɪғ ʏᴏᴜ ғᴀᴄᴇ ᴀɴʏ ᴘʀᴏʙʟᴇᴍs!
**"""




@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{app.username}?startgroup=true")
        ],
        [
          InlineKeyboardButton("Channel", url="https://t.me/Star_Boy_96_vibes"),
          InlineKeyboardButton("All bot", url="https://t.me/Star_Boy_96_vibes/260"),
          ],
               [
                InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/Star_light_10"),

],
[
              InlineKeyboardButton("Shinhari music", url=f"https://t.me/Shinhari_Musicbot"),
              InlineKeyboardButton("Chat Bot", url=f"https://t.me/Ladyhinata_chatbot"),
              ],
              [
              InlineKeyboardButton("Paid Restricted bot ", url=f"https://t.me/Starboy_Restricted_bot"),
InlineKeyboardButton("Free Restricted bot", url=f"https://t.me/Starboy_Save_Private_Content_Bot"),
]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo=config.START_IMG_URL,
        caption=start_txt,
        reply_markup=reply_markup
    )




@app.on_message(
    filters.command(
        ["hi", "hii", "hello", "hui", "good", "gm", "ok", "bye", "welcome", "thanks"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & filters.group
)
async def bot_check(_, message):
    chat_id = message.chat.id
    await add_served_chat(chat_id)
