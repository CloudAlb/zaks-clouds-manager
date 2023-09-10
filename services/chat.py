from helpers.__exceptions import EventChatNotFoundException

from telethon.events import NewMessage

def get_chat_from_event(event: NewMessage.Event):
    if (not event.chat): raise EventChatNotFoundException
    return event.chat
