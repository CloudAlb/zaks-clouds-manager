from dotenv import dotenv_values
from telethon.tl.custom.message import Message

import helpers.constants as constants
from helpers.__exceptions import CommandArgsRequiredException, MissingDotEnvField, EventPatternMatchNotFoundException, MessageNotFoundException

from telethon import TelegramClient, events
from telethon.events.messageedited import NewMessage

from services.message import check_channel_messages_duplications, update_last_twitter_received_url
from services.url import modify_url_message

config = dotenv_values(".env")

api_id = config.get("API_ID")
if (not api_id): raise MissingDotEnvField
api_id_int = int(api_id)
api_hash = str(config.get("API_HASH"))

client_name_user=config.get('CLIENT_NAME_USER_DRAGONBELLY')
client_name_bot=config.get('CLIENT_NAME_BOT_ZAK')

if (not api_hash): raise MissingDotEnvField
if (not client_name_user): raise MissingDotEnvField
if (not client_name_bot): raise MissingDotEnvField

client = TelegramClient(client_name_user, api_id_int, api_hash)
bot = TelegramClient(client_name_bot, api_id_int, api_hash)

@client.on(events.NewMessage(pattern=constants.URL_REGEX))
async def modify_url_message_handler(event: NewMessage.Event):
    await modify_url_message(client, bot, event)

@client.on(events.NewMessage(pattern='^/[a-zA-Z0-9_]+(\\s\\d+)?$'))
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
        case 'check_channel_messages_duplications':
            print('Initializing "check_channel_messages_duplications" function')
            await check_channel_messages_duplications(client, event)
        case 'twitter':
            if (not command_args): raise CommandArgsRequiredException
            await update_last_twitter_received_url(client, event, command_args)

client.start()
bot.start()
client.run_until_disconnected()
