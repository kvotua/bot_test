import asyncpg
from core.utils.user import *

class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_user(self, user_id, username, firstname, lastname):
        query = f"INSERT INTO users (user_id, username, firstname, lastname) VALUES ({user_id}, '{username}', '{firstname}', '{lastname}') "\
                f"ON CONFLICT (user_id) DO UPDATE SET username='{username}', firstname='{firstname}', lastname='{lastname}';"
        await self.connector.execute(query)
    
    async def get_user(self, user_id):
        query = f"SELECT * FROM users WHERE user_id={user_id};"
        user: User = await self.connector.fetchrow(query=query, record_class=User)
        user.update_data()
        return user
    