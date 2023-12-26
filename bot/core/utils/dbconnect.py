import asyncpg
from core.utils.models import *

class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_user(self, user_id, username, firstname, lastname, role):
        query = f"INSERT INTO users (user_id, username, firstname, lastname, role) VALUES ({user_id}, '{username}', '{firstname}', '{lastname}', '{role}') "\
                f"ON CONFLICT (user_id) DO UPDATE SET username='{username}', firstname='{firstname}', lastname='{lastname}';"
        await self.connector.execute(query)
    
    async def get_user(self, user_id):
        query = f"SELECT * FROM users WHERE user_id={user_id};"
        user: User = await self.connector.fetchrow(query=query, record_class=User)
        user.update_data()
        return user
    
    async def user_exist(self, user_id):
        query = f"SELECT user_id FROM users WHERE user_id={user_id};"
        id = await self.connector.fetchrow(query=query)
        if id == None:
            return False
        id = id['user_id']
        return id
    
    async def update_user(self, user_id, username, firstname, lastname, role):
        self.add_user(user_id, username, firstname, lastname, role)

    async def company_exist(self, company_id):
        query = f"SELECT id FROM company WHERE id={company_id}"
        company = await self.connector.fetchrow(query=query, record_class=Company)
        if company == None:
            return False
        return company['id']
    
    async def add_company(self, ip_name, user_id):
        query = f'INSERT INTO company (ip_name) VALUES ({ip_name});'
        await self.connector.execute(query)
        query = f'SELECT id FROM company WHERE ip_name={ip_name}'
        id = (await self.connector.fetchrow(query))['id']
        query = f'INSERT INTO users_company (user_id, company_id) VALUES ({user_id}, {id});'
        await self.connector.execute(query)
        return id

    async def user_company_exist(self, user_id) -> bool:
        query = f'SELECT company_id FROM users_company WHERE user_id={user_id}'
        company = await self.connector.fetchrow(query=query)
        if company == None:
            return False
        return company['company_id']
    
    async def get_all_point_company(self, user_id):
        company_id = await self.user_company_exist(user_id)
        if company_id == None:
            return None
        query = f'SELECT * FROM point_company WHERE company_id={company_id}'
        points = await self.connector.fetch(query=query, record_class=Point)
        if points.__len__() == 0:
            return None
        for i in range(len(points)):
            points[i].update_data()            
        return points
    
    async def get_point(self, id):
        query = f'SELECT * FROM point_company WHERE id={id}'
        point = await self.connector.fetchrow(query=query, record_class=Point)
        if point == None:
            return None
        point.update_data()
        return point 

    async def save_poduct(self, name):
        query = f'INSERT INTO products (name) VALUES ({name})'
        await self.connector.execute(query=query)