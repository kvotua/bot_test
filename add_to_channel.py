from pyrogram import Client

from env import *

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
   
    about_skyfox = client.get_users('skyfox')


file1 = open("data_output/about_me.json", "w") 
file1.write(str(about_me))

file2 = open("data_output/about_skyfox.json", "w") 
file2.write(str(about_skyfox))

file1.close()
file2.close()

with client:
    kvotua_channel = client.get_chat(channel_kvotua)
    link1 = (client.create_chat_invite_link(chat_id=channel_kvotua, name='Давай дружить!')).invite_link

user = input("Введите username пользователя которого хотите добавить: ")
with client:
    client.send_message(29849657, link1)
    

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