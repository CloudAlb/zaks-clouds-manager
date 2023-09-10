import re, asyncio

from dotenv import dotenv_values

from telethon import TelegramClient, Button
from telethon.events import NewMessage
from telethon.tl import types
from telethon.tl.custom.message import Message

from services.chat import get_chat_from_event

import helpers.constants as constants
from helpers.__exceptions import MessageNotFoundException, EventChatMessageNotFoundException

config = dotenv_values(".env")

class UrlNotChangedException(Exception):
    def __init__(self, message="URL wasn't changed"):
        self.message = message
        super().__init__(self.message)

class DomainParamNotInDomainsDict(Exception):
    def __init__(self, message="The domain used for \"is_modified_domain_url\" is not valid"):
        self.message = message
        super().__init__(self.message)

ALLOWED_DOMAIN_MODIFICATIONS = {
    "twitter.com": "vx",
    "furaffinity.net": "fx",
}

def is_url(text):
    if (re.match(constants.URL_REGEX, text)):
        return True
    return False

def is_modified_url(url):
    for domain, modification in ALLOWED_DOMAIN_MODIFICATIONS.items():
        if re.match(f'^https?://(?:www\\.)?{modification}{domain}/.*$', url):
            return True
    return False

def is_modified_domain_url(url, domain):
    if (domain not in ALLOWED_DOMAIN_MODIFICATIONS):
        raise DomainParamNotInDomainsDict

    for domain, modification in ALLOWED_DOMAIN_MODIFICATIONS.items():
        if re.match(f'^https?://(?:www\\.)?{modification}{domain}/.*$', url):
            return True
    return False

def apply_domain_modifications(url: str):
    for domain, modification in ALLOWED_DOMAIN_MODIFICATIONS.items():
        if re.match(f'^https?://(?:www\\.)?{domain}/.*$', url):
            modified_url = re.sub(f'^https?://(?:www\\.)?{domain}', f'https://{modification}{domain}', url)
            modified_url = modified_url.split('?')[0]  # Remove query parameters
            return modified_url
    return False

async def modify_url_message(client: TelegramClient, bot: TelegramClient, event: NewMessage.Event):
    chat = await get_chat_from_event(event)

    original_message: Message = event.message
    if (not original_message): raise MessageNotFoundException

    original_message_text = original_message.text
    if (not original_message_text): raise EventChatMessageNotFoundException

    if (is_modified_url(original_message_text)): return

    modified_url = apply_domain_modifications(original_message_text)
    if (not modified_url): raise UrlNotChangedException

    await asyncio.sleep(0.1)

    if isinstance(chat, types.Channel):
        await original_message.delete()

        await bot.send_message(
            entity=chat.id,
            message=modified_url,
            buttons=[Button.url(text='Source', url=original_message_text.split("?")[0])]
        )
    else:
        # await client.edit_message(
        #     entity=chat,
        #     message=original_message,
        #     text=modified_url,
        #     buttons=message_buttons
        # )

        await original_message.edit(
            text=modified_url,
        )
