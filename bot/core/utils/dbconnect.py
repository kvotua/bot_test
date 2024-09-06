import asyncpg
import datetime
import logging
from core.utils.models import *


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_user(
        self,
        user_id,
        username,
        firstname,
        lastname,
        role,
    ):
        query = (
            f"INSERT INTO users (user_id, username, firstname, lastname, role, stuff) VALUES ({user_id}, '{username}', '{firstname}', '{lastname}', '{role}', '{False}') "
            f"ON CONFLICT (user_id) DO UPDATE SET username='{username}', firstname='{firstname}', lastname='{lastname}';"
        )
        await self.connector.execute(query)

    async def get_user(self, user_id):
        query = f"SELECT * FROM users WHERE user_id={user_id};"
        user: User = await self.connector.fetchrow(query=query, record_class=User)
        user.update_data()
        return user
    
    async def update_products(self, products):
        await self.connector.execute(f"DELETE FROM products")
        data = [(obj['name'], obj['place']) for obj in products]
        logging.info(products)
        logging.info(data)
        insert_query = f"INSERT INTO products (name, place) VALUES ($1, $2)"
        await self.connector.executemany(insert_query, data)
        logging.info('обновление')
    
    async def get_user_by_company(self, company_id):
        query = f"SELECT user_id FROM users_company WHERE company_id={company_id};"
        user_id_record = await self.connector.fetchrow(query=query)
        user_id: int = user_id_record["user_id"]
        logging.info(f"user_id: {user_id} user_id_record: {user_id_record}")
        user: User = await self.get_user(user_id)
        if user == None:
            return False
        else:
            return user
    
    async def update_user_stuff(self, user_id, point_id):
        query = f"UPDATE users SET stuff='{True}', point_id='{point_id}' WHERE user_id='{user_id}'"
        await self.connector.execute(query=query)

    async def user_exist(self, user_id):
        query = f"SELECT * FROM users WHERE user_id={user_id};"
        user = await self.connector.fetchrow(query=query, record_class=User)
        if user == None:
            return False
        else:
            user.update_data()
            return user

    async def update_user(self, user_id, username, firstname, lastname, role):
        self.add_user(user_id, username, firstname, lastname, role)

    async def company_exist(self, company_id):
        query = f"SELECT id FROM company WHERE id={company_id}"
        company = await self.connector.fetchrow(query=query, record_class=Company)
        if company == None:
            return False
        return company["id"]

    async def get_company(self, company_id):
        query = f"SELECT * FROM company WHERE id={company_id}"
        company = await self.connector.fetchrow(query=query, record_class=Company)
        if company == None:
            return False
        company.update_data()
        return company
    
    async def get_company_by_name(self, company_name):
        query = f"SELECT * FROM company WHERE legal_entity='{company_name}'"
        company = await self.connector.fetchrow(query=query, record_class=Company)
        if company == None:
            return False
        company.update_data()
        return company

    async def get_all_company(self):
        query = f"SELECT * FROM company"
        companys = await self.connector.fetch(query=query, record_class=Company)
        if companys.__len__() == None:
            return False
        for i in range(len(companys)):
            companys[i].update_data()
        return companys

    async def add_company(self, kind_name, user_id):
        kind_name = kind_name.upper()
        query = f"INSERT INTO company (legal_entity) VALUES ('{kind_name}')"
        await self.connector.execute(query)
        query = f"SELECT id FROM company WHERE legal_entity='{kind_name}'"
        id_record = await self.connector.fetchrow(query)
        id = id_record["id"]
        query = (
            f"INSERT INTO users_company (user_id, company_id) VALUES ({user_id}, {id});"
        )
        await self.connector.execute(query)
        return id

    async def add_user_in_exist_company(self, user_id, company_id):
        if not await self.user_exist(user_id):
            self.add_user(
                user_id, username=None, firstname=None, lastname=None, role="client"
            )
        query = (
            f"INSERT INTO users_company (user_id, company_id) VALUES ({user_id}, {company_id});"
        )
        await self.connector.execute(query)
        return company_id

    async def user_company_exist(self, user_id) -> bool:
        query = f"SELECT company_id FROM users_company WHERE user_id={user_id}"
        company = await self.connector.fetchrow(query=query)
        if company == None:
            return False
        return company["company_id"]

    async def get_all_point_company(self, user_id: int):
        company_id = await self.user_company_exist(user_id)
        if company_id == None:
            return None
        query = f"SELECT * FROM point_company WHERE company_id={company_id}"
        points = await self.connector.fetch(query=query, record_class=Point)
        if points.__len__() == 0:
            return None
        for i in range(len(points)):
            points[i].update_data()
        return points
    
    async def get_all_point_company_by_company_id(self, company_id: int):
        query = f"SELECT * FROM point_company WHERE company_id={company_id}"
        points = await self.connector.fetch(query=query, record_class=Point)
        if points.__len__() == 0:
            return None
        for i in range(len(points)):
            points[i].update_data()
        return points

    async def get_point(self, id):
        query = f"SELECT * FROM point_company WHERE id={id}"
        point = await self.connector.fetchrow(query=query, record_class=Point)
        if point == None:
            return None
        point.update_data()
        return point

    async def update_name_point(self, name_old, name_new):
        query = f"UPDATE point_company SET name='{name_new}' WHERE name='{name_old}'"
        await self.connector.execute(query=query)

    async def update_address_point(self, name, city, address):
        query = f"UPDATE point_company SET city='{city}', address='{address}' WHERE name='{name}'"
        await self.connector.execute(query=query)

    async def get_point_by_name(self, user_id: int, name: str):
        points = await self.get_all_point_company(user_id)
        for i in points:
            if i.name == name:
                return i.id
        return None

    async def add_point(self, name, address, city, user_id):
        company_id = await self.user_company_exist(user_id)
        if company_id == None:
            return None
        query = f"INSERT INTO point_company (name, address, city, company_id, date_reg) VALUES ('{name}', '{address}', '{city}', {company_id}, '{datetime.datetime.now():%Y-%m-%d %H:%M:%S}')"
        await self.connector.execute(query=query)

    async def save_poduct(self, names, place):
        end_s = names[-1]
        if end_s == " ":
            names = names[:-1]
        query = (
            f"INSERT INTO products (name, place) VALUES ('{names}', ({int(place)}));"
        )
        await self.connector.execute(query=query)

    async def delete_product(self, id):
        query = f"DELETE FROM products WHERE id={id}"
        await self.connector.execute(query=query)

    async def change_place(self, product, place):
        query = f"UPDATE products SET place={int(place)} WHERE name='{product}'"
        await self.connector.execute(query=query)

    async def exist_name_product(self, name):
        query = f"SELECT name FROM products WHERE name='{name}'"
        records = await self.connector.fetch(query=query)
        if records.__len__() == 0:
            return False
        return True

    async def get_products(self):
        query = f"SELECT * FROM products"
        products_record = await self.connector.fetch(query=query, record_class=Product)
        if products_record.__len__() == 0:
            return None
        for i in range(len(products_record)):
            products_record[i].update_data()
        return products_record

    status = ["created", "processed", "awaiting pickup", "pickup", "delivered"]

    async def create_order(
        self, user_id: int, company_id: int, is_delivery: bool, date
    ):
        temp = str(date).replace("/", "-")
        date_order = datetime.datetime.strptime(temp, "%d-%m-%Y").date()
        query = f"INSERT INTO orders (date_create_order, user_id, status, company_id, is_delivery, date_delivery) VALUES ('{datetime.datetime.now():%Y-%m-%d %H:%M:%S}', {user_id}, '{self.status[0]}', {company_id}, {is_delivery}, '{date_order}') RETURNING id;"
        order_id = await self.connector.fetchrow(query)
        return order_id["id"]

    async def get_order(self, order_id):
        query = f"SELECT * FROM orders WHERE id={order_id}"
        order = await self.connector.fetchrow(query=query, record_class=Order)
        order.update_data()
        return order

    async def save_bucket_by_order(self, order_id: int, bucket: dict):
        for key, value in bucket.items():
            if value.isdigit():
                query = f"INSERT INTO orders_products (order_id, count, product_name) VALUES ({order_id}, {value}, '{key}' )"
                await self.connector.execute(query=query)

    async def get_bucket(self, order_id):
        query = (
            f"SELECT count, product_name FROM orders_products WHERE order_id={order_id}"
        )
        bucket = await self.connector.fetch(query=query)
        new_bucket = {}
        for item in bucket:
            new_bucket[item["product_name"]] = item["count"]
        return new_bucket

    async def save_message(
        self,
        user_id: int,
        message_id: int,
        text: str,
        delete: bool,
        is_callback: str,
    ):
        query = f"INSERT INTO message (message_id, user_id, date, delete, text, who_is) VALUES ({message_id}, {user_id}, '{datetime.datetime.now():%Y-%m-%d %H:%M:%S}', {delete}, '{text}', '{is_callback}');"
        await self.connector.execute(query)

    async def get_messages_by_user(self, user_id: int):
        query = (
            f"SELECT id, message_id, delete, text FROM message WHERE user_id={user_id};"
        )
        messages = await self.connector.fetch(query=query)
        return messages

    async def delete_message(self, message):
        id = message["id"]
        query = f"DELETE FROM message WHERE id={id}"
        await self.connector.execute(query=query)
