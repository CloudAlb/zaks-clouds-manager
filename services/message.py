import re, asyncio

from typing import Dict

from helpers.__exceptions import EventChatNotFoundException, MessageNotFoundException

from telethon import TelegramClient
from telethon.events import NewMessage

from telethon.tl.custom import Message

from services.url import is_modified_domain_url

async def get_channel_messages(client: TelegramClient, event: NewMessage.Event) -> Dict[int, str]:
    if (not event.chat): raise EventChatNotFoundException

    messages = {}

    message: Message
    async for message in client.iter_messages(event.chat, reverse=True):
        messages[message.id] = message.text

    return messages

async def check_channel_messages_duplications(client: TelegramClient, event: NewMessage.Event):
    if (not event.chat): raise EventChatNotFoundException

    channel_messages = await get_channel_messages(client, event)

    first_occurrence = {}
    second_occurrence = {}

    for message_id, message_text in channel_messages.items():
        if not message_text:
            continue

        if message_text in first_occurrence:
            if message_text in second_occurrence.values():
                second_occurrence[message_id].append(message_text)
            else:
                second_occurrence[message_id] = [message_text]
        else:
            first_occurrence[message_id] = message_text

    if not len(first_occurrence):
        await client.send_message(event.chat, 'There are no duplicated messages in this channel.')
        return

    await client.send_message(event.chat, 'There are duplicated messages in this channel.')
    for messages_ids, message_text in second_occurrence.items():
        original_message_id = list(first_occurrence.keys())[list(first_occurrence.values()).index(message_text)]
        await client.send_message(event.chat, reply_to=original_message_id, message='This message right here:')

        for message_id in messages_ids:
            await client.send_message(event.chat, reply_to=message_id, message='is duplicated by this one.')
    await client.send_message(event.chat, 'End of duplicated messages.')


class CannotFindLastMessageException(Exception):
    def __init__(self, message="Cannot find last message sent by the user"):
        self.message = message
        super().__init__(self.message)

class LatestMessageIsNotValidTwitterUrl(Exception):
    def __init__(self, message="The latest message the user sent in the chat is not a valid Twitter URL"):
        self.message = message
        super().__init__(self.message)

async def update_last_twitter_received_url(client: TelegramClient, event: NewMessage.Event, command_arg):
    if (not event.chat): raise EventChatNotFoundException

    original_message: Message = event.message
    if (not original_message): raise MessageNotFoundException

    latest_message_id = None
    latest_message_text = None
    async for message in client.iter_messages(
        entity=event.chat,
        from_user='me',
        limit=1,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=1,
    ):
        latest_message_id = message.id
        latest_message_text = message.text

    if (not latest_message_id or not latest_message_text): raise CannotFindLastMessageException

    if (not is_modified_domain_url(latest_message_text, 'twitter.com')): raise LatestMessageIsNotValidTwitterUrl

    await asyncio.sleep(1)

    await original_message.delete()

    command_arg = int(command_arg)
    if (command_arg < 0):
        return

    photo_pattern_route_regex = r'/photo/\d+$'
    latest_message_text_without_photo_route = re.sub(photo_pattern_route_regex, '', latest_message_text)

    if (command_arg == 0):
        await client.edit_message(entity=event.chat, message=latest_message_id, text=latest_message_text_without_photo_route)
        return

    modified_url = f"{latest_message_text_without_photo_route}/photo/{command_arg}"

    await client.edit_message(entity=event.chat, message=latest_message_id, text=modified_url)
