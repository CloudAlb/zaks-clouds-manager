from helpers.__exceptions import MessageNotFoundException

from telethon.tl.custom.message import Message

def get_message_from_event(event):
    message: Message = event.message
    if (not message): raise MessageNotFoundException

    return message

async def send_working_on_it_message(client, chat):
    working_on_it_message = await client.send_message(
        entity=chat,
        message='working on it...'
    )

    return working_on_it_message
