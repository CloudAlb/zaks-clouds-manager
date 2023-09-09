import os, re, asyncio, tempfile

from datetime import date

from typing import Dict

from helpers.__exceptions import EventChatNotFoundException, MessageNotFoundException

from telethon import TelegramClient, Button
from telethon.events import NewMessage
from telethon.tl.custom import Message

from services.url import apply_domain_modifications, is_modified_domain_url, is_url

def is_event_message_date_before_bot_connection_date(message_event: NewMessage.Event, bot_connection_date: date):
    if (not message_event.chat): raise EventChatNotFoundException

    message: Message = message_event.message
    if (not message): raise MessageNotFoundException

    assert message.date

    if message.date.now() < bot_connection_date:
        return True
    return False

async def get_channel_messages(client: TelegramClient, chat) -> Dict[int, str]:
    messages = {}

    message: Message
    async for message in client.iter_messages(chat, reverse=True):
        if (not message.text): continue

        messages[message.id] = message.text

    return messages

async def check_channel_messages_duplications(client: TelegramClient, chat):
    channel_messages = await get_channel_messages(client, chat)

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
        await client.send_message(chat, 'There are no duplicated messages in this channel.')
        return

    await client.send_message(chat, 'There are duplicated messages in this channel.')
    for messages_ids, message_text in second_occurrence.items():
        original_message_id = list(first_occurrence.keys())[list(first_occurrence.values()).index(message_text)]
        await client.send_message(
            entity=chat,
            message='This message right here',
            reply_to=original_message_id
        )

        for message_id in messages_ids:
            await client.send_message(
                entity=chat,
                message='is duplicated by this one:',
                reply_to=message_id
            )

    await client.send_message(
        entity=chat,
        message='End of duplicated messages.'
    )

    await client.send_message(
        entity=chat,
        message='Click on this button to dismiss all the messages.',
        buttons=[Button.text(text='Dismiss')]
    )

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

    await asyncio.sleep(0.1)

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

async def get_all_messages_as_file(client: TelegramClient, bot: TelegramClient, event: NewMessage.Event):
    if (not event.chat): raise EventChatNotFoundException
    chat = event.chat

    original_message: Message = event.message
    if (not original_message): raise MessageNotFoundException
    await original_message.delete()

    messages = await get_channel_messages(client, chat)

    working_on_it_message = await client.send_message(
        entity=chat,
        message='Working on it...'
    )

    _, temp_file = tempfile.mkstemp(prefix= 'channel_messages_', suffix=".txt", text=True)

    try:
        with open(temp_file, 'w') as file:
            for message in messages.values():
                if (not message): continue
                if (not is_url(message)): continue

                file.write(message + '\n')
    except:
        raise Exception

    await client.delete_messages(
        entity=chat,
        message_ids=working_on_it_message
    )

    try:
        if os.path.getsize(temp_file) == 0:
            await client.send_message(
                entity=chat,
                message='Sorry, I was not able to retrieve any messages'
            )
            
            return

        await client.send_message(
            entity=chat,
            message='Done!'
        )

        await client.send_file(
            entity=chat,
            file=temp_file,
            caption='Here are all the messages of this channel in a file'
        )
    except:
        raise Exception
    finally:
        os.remove(temp_file)

async def format_all_messages(client: TelegramClient, event: NewMessage.Event):
    if (not event.chat): raise EventChatNotFoundException
    chat = event.chat

    original_message: Message = event.message
    await original_message.delete()

    working_on_it_message = await client.send_message(
        entity=chat,
        message='Working on it...'
    )

    if (not original_message): raise MessageNotFoundException
    messages = await get_channel_messages(client, chat)

    modified_messages = {}

    for message_id, message_text in messages.items():
        modified_text = apply_domain_modifications(message_text)

        if (modified_text):
            modified_messages[message_id] = modified_text

    for message_id, new_message in modified_messages.items():
        await client.edit_message(
            entity=chat,
            message=message_id,
            text=new_message
        )

    await client.delete_messages(
        entity=chat,
        message_ids=working_on_it_message
    )

    if (not len(modified_messages)):
        await client.send_message(
            entity=chat,
            message='No messages were affected.'
        )

        return

    await client.send_message(
        entity=chat,
        message='Done!'
    )

    await client.send_message(
        entity=chat,
        message='These messages where affected:'
    )

    for message_id, new_message in modified_messages.items():
        await client.send_message(
            entity=chat,
            message=f'ID: {message_id}',
            reply_to=message_id
        )
