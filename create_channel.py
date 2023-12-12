import os
import json

from dotenv import load_dotenv

from pyrogram import Client
from pyrogram.raw.functions.messages import Search
from pyrogram.raw.types import InputPeerSelf, InputMessagesFilterEmpty
from pyrogram.raw.types.messages import ChannelMessages

load_dotenv(dotenv_path='.env')

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
channel_kvotua = os.getenv('test_channels')
channel_id = os.getenv('test_channel_id')

client = Client(
    'my_account',
    api_id=api_id,
    api_hash=api_hash
)

with client:
    client.send_sticker(
    chat_id="me", 
    sticker="CAACAgIAAxkBAAEoNxBleGTk8ZnvZwO7H7mvCP5AaWs89gACwRgAAn2IqUiOzhz_SUBYkDME"),
    about_me = client.get_me()
    about_skyfox = client.get_users('skyfox1994')


file1 = open("data_output/about_me.json", "w") 
file1.write(str(about_me))

file2 = open("data_output/about_skyfox.json", "w") 
file2.write(str(about_skyfox))

file1.close()
file2.close()

with client:
    kvotua_channel = client.get_chat(channel_kvotua)
    link1 = (client.create_chat_invite_link(chat_id=channel_kvotua, name='Давай дружить!')).invite_link
    client.send_message('skyfox1994', link1)

# with client:
#     client.send(
#         functions.channels.InviteToChannel(
#             channel=client.resolve_peer("kyruso"), # ID or Username
#             users=[ # The users you want to invite
#                 client.resolve_peer("skyfox1994"), # By username
#                 client.resolve_peer("andreymaltc"), # By phone number
#             ]
#         )
#     )