from telethon.events.newmessage import NewMessage

async def get_channel_id(event: NewMessage.Event) -> int:
    assert event.chat
    assert event.chat.id
    return event.chat.id
