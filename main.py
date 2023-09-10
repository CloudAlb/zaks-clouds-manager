import os, logging
# from datetime import datetime
from dotenv import dotenv_values
from telethon.tl.custom.message import Message

import helpers.constants as constants
from helpers.__exceptions import CommandArgsRequiredException, MissingDotEnvField, EventPatternMatchNotFoundException, MessageNotFoundException, EnvironmentEnvVarNotDefined

from telethon import TelegramClient, events
from telethon.events.messageedited import NewMessage
from services.__utils__.types import assert_is_digit

from services.message import check_channel_messages_duplications, search_message, update_last_twitter_received_url, get_all_messages_as_file, format_all_messages
from services.url import modify_url_message

environment = os.environ.get('ENVIRONMENT')

api_id = None
api_id_int = None
api_hash = None
bot_token = None
phone_number = None

if (environment == 'development'):
    logging.basicConfig(level=logging.DEBUG)

    config = dotenv_values(".env")
    api_id = config.get("API_ID")
    api_hash = config.get("API_HASH")
    bot_token = config.get("BOT_TOKEN")
    phone_number = config.get("PHONE_NUMBER")
elif (environment == 'production'):
    with open('/secret/API_ID', 'r') as file:
        api_id = file.read().replace('\n', '')

    with open('/secret/API_HASH', 'r') as file:
        api_hash = file.read().replace('\n', '')

    with open('/secret/BOT_TOKEN', 'r') as file:
        bot_token = file.read().replace('\n', '')

    with open('/secret/PHONE_NUMBER', 'r') as file:
        phone_number = file.read().replace('\n', '')
else:
    raise EnvironmentEnvVarNotDefined

if (not api_id): raise MissingDotEnvField
if (not api_hash): raise MissingDotEnvField
if (not bot_token): raise MissingDotEnvField
if (not phone_number): raise MissingDotEnvField

api_id = int(api_id)
api_hash = str(api_hash)
bot_token = str(bot_token)

client = TelegramClient('user', api_id, api_hash)
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# clients_connection_datetime = datetime.now()

@client.on(events.NewMessage(pattern=constants.URL_REGEX))
async def modify_url_message_handler(event: NewMessage.Event):
    await modify_url_message(client, bot, event)

@client.on(events.NewMessage(pattern=r'^/[a-zA-Z0-9_]+(\s[a-zA-Z0-9_]+)?$'))
async def get_command(event: NewMessage.Event):

    if (not event.pattern_match): raise EventPatternMatchNotFoundException

    original_message: Message = event.message
    if (not original_message): raise MessageNotFoundException

    command_info = event.pattern_match.group(0)
    command_info = command_info.replace('/', '')

    command_info_split = command_info.split(' ')
    command_str = command_info_split[0]

    command_args = None
    if (len(command_info_split) > 1): command_args = command_info_split[-1]

    print("Captured command: {}".format(command_str))

    if (command_args): print("Captured command args: {}".format(command_args))

    match command_str:
        case 'get_all_messages_as_file':
            await get_all_messages_as_file(client, bot, event)
        case 'format_all_messages':
            await format_all_messages(client, event)
        case 'check_channel_messages_duplications':
            await check_channel_messages_duplications(client, event)
        case 'twitter':
            if (not command_args): raise CommandArgsRequiredException
            assert_is_digit(command_args)
            await update_last_twitter_received_url(client, event, command_args)
        case 'search':
            if (not command_args): raise CommandArgsRequiredException
            await search_message(client, event, command_args)

def start():
    client.start()
    bot.start()
    print("🚀 App started!")
    client.run_until_disconnected()

start()
