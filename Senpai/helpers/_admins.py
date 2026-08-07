
from pyrogram import enums, filters, types
from pyrogram.enums import ChatMemberStatus


async def _is_admin(_, client, message: types.Message) -> bool:
    if message.chat.type == enums.ChatType.PRIVATE:
        return False
    if not message.from_user:
        return False
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
    except Exception:
        return False
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


admin_filter = filters.create(_is_admin)
