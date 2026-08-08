
from pyrogram import enums, filters, types
from pyrogram.enums import ChatMemberStatus
from loguru import logger


async def _is_admin(_, client, message: types.Message) -> bool:
    if message.chat.type == enums.ChatType.PRIVATE:
        return False
    if not message.from_user:
        return False
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
    except Exception as e:
        logger.debug(f"Failed to check admin status: {e}")
        return False
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


admin_filter = filters.create(_is_admin)
