import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
bot_token = os.getenv("bot_token")
user_id_for_push = os.getenv("user_id_admin")
channel_kvotua = os.getenv("test_channel_id")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
channel_ponarth = os.getenv("channel_ponarth")
spreadsheetid = os.getenv("spreadsheetid")
# host = os.environ['HOST_TRUE']
