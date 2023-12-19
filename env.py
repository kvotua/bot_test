import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
bot_token = os.getenv('bot_token')
user_id_for_push=os.getenv('user_id_admin')
channel_kvotua=os.getenv('test_channel_id')