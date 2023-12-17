import os
from datetime import datetime, date
from dotenv import load_dotenv

from pyrogram import Client
from pyrogram.raw.types import InputPhoneContact
from pyrogram.raw.base import InputContact

load_dotenv(dotenv_path='.env')

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
channel_kvotua = os.getenv('test_channels')
channel_id = os.getenv('test_channel_id')


phone_number = "+79965229495"

client = Client(
    'my_account',
    api_id=api_id,
    api_hash=api_hash
)

with client:
   client.send_sticker('skyfox1994', 'CAACAgIAAxkBAAEoNxBleGTk8ZnvZwO7H7mvCP5AaWs89gACwRgAAn2IqUiOzhz_SUBYkDME')