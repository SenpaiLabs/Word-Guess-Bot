
from pyrogram import filters, types, enums

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._dataclass import User
from Senpai.core.lang import lang
from Senpai.helpers._inline import inline
from config import config
@app.on_message(filters.command("help"))
@lang.language()
async def help_command(_, m: types.Message):
    text = m.lang.get("help_menu", "Help Menu")
    reply_markup = inline.help_markup(m.lang)
    await m.reply_text(text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex(r"^help(\s+(.*))?$"))
@lang.language()
async def help_callback(_, query: types.CallbackQuery):
    data = query.data.split(maxsplit=1)
    
    if len(data) == 1 or data[1] == "back":
        text = query.lang.get("help_menu", "Help Menu")
        reply_markup = inline.help_markup(query.lang)
        
        try:
            if query.message.photo or query.message.video:
                await query.message.delete()
                await app.send_message(query.message.chat.id, text, reply_markup=reply_markup)
            else:
                await query.edit_message_text(text, reply_markup=reply_markup)
        except Exception:
            pass
        
    elif data[1] == "close":
        try:
            await query.message.delete()
        except Exception:
            pass
        
    else:
        category = data[1]
        text_key = f"help_text_{category}"
        text = query.lang.get(text_key, f"Help for {category.capitalize()}")
        
        reply_markup = inline.help_markup(query.lang, back=True)
        try:
            if query.message.photo or query.message.video:
                await query.message.delete()
                await app.send_message(query.message.chat.id, text, reply_markup=reply_markup)
            else:
                await query.edit_message_text(text, reply_markup=reply_markup)
        except Exception:
            pass


@app.on_message(filters.command("start"))
@lang.language()
async def start_cmd(_, m: types.Message):
    if len(m.command) > 1 and m.command[1] == "help":
        return await help_command(_, m)

    if m.from_user:
        await db.register_user(User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username))
        
        if config.LOGGER_ID and m.chat.type == enums.ChatType.PRIVATE:
            try:
                log_text = m.lang.get("log_new_user", "log_new_user").format(
                    user_id=m.from_user.id,
                    user_mention=m.from_user.mention
                )
                await app.send_message(
                    config.LOGGER_ID, 
                    log_text
                )
            except Exception:
                pass

    me = await app.get_me()
    
    if m.chat.type == enums.ChatType.PRIVATE:
        text = m.lang.get("start_pm", "start_pm").format(name=m.from_user.first_name)
        reply_markup = inline.start_key(m.lang, me.username, private=True)
    else:
        text = m.lang.get("start_gc", "start_gc")
        reply_markup = inline.start_key(m.lang, me.username)

    if config.START_IMG:
        await m.reply_photo(
            photo=config.START_IMG,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await m.reply_text(text, reply_markup=reply_markup)



@app.on_message(filters.new_chat_members)
@lang.language()
async def on_new_chat_members(_, m: types.Message):
    if not config.LOGGER_ID:
        return
        
    me = await app.get_me()
    for user in m.new_chat_members:
        if user.id == me.id:
            adder = m.from_user
            user_id = adder.id if adder else 0
            user_mention = adder.mention if adder else "Unknown"
            
            try:
                log_text = m.lang.get("log_new_chat", "log_new_chat").format(
                    chat_id=m.chat.id,
                    chat_title=m.chat.title,
                    user_id=user_id,
                    user_mention=user_mention
                )
                await app.send_message(
                    config.LOGGER_ID, 
                    log_text
                )
            except Exception:
                pass


@app.on_message(filters.left_chat_member)
@lang.language()
async def on_left_chat_member(_, m: types.Message):
    me = await app.get_me()
    if m.left_chat_member.id == me.id:
        try:
            await db.remove_group(m.chat.id)
            if config.LOGGER_ID:
                remover = m.from_user
                user_id = remover.id if remover else 0
                user_mention = remover.mention if remover else "Unknown"
                
                log_text = m.lang.get("log_left_chat", "❌ **Bot Removed From Group!**\n\n**Chat:** {chat_title} (`{chat_id}`)\n**Removed By:** {user_mention} (`{user_id}`)").format(
                    chat_id=m.chat.id,
                    chat_title=m.chat.title,
                    user_id=user_id,
                    user_mention=user_mention
                )
                await app.send_message(
                    config.LOGGER_ID, 
                    log_text
                )
        except Exception:
            pass
