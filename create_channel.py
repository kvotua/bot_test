from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram.raw import functions, types
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

user_auth = Client(
    'my_account',
    api_id=api_id,
    api_hash=api_hash
)

def my_function(client, message):
    print(message.text)


my_handler = MessageHandler(my_function)
user_auth.add_handler(my_handler)

user_auth.run()

# with user_auth:
#     user_auth.send(
#         functions.channels.InviteToChannel(
#             channel=user_auth.resolve_peer("kyruso"), # ID or Username
#             users=[ # The users you want to invite
#                 user_auth.resolve_peer("skyfox1994"), # By username
#                 user_auth.resolve_peer("andreymaltc"), # By phone number
#             ]
#         )
#     )