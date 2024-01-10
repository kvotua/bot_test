from asyncpg import Record
from aiogram.types import KeyboardButton, KeyboardButtonPollType, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import datetime
from aiogram.filters.callback_data import CallbackData

class User(Record):
    user_id: int
    username: str
    firstname: str
    lastname: str
    role: str

    def update_data(self):
        self.user_id=self['user_id']
        self.username=self['username']
        self.firstname=self['firstname']
        self.lastname=self['lastname']
        self.role=self['role']

    def __str__(self):
        return f'user_id:{self.user_id} username:{self.username} firstname:{self.firstname} lastname:{self.lastname} role:{self.role}'

class Company(Record):
    id: int
    ip_name: str
    users: list

    def update_data(self):
        self.id = self['id']
        self.ip_name = self['ip_name']
    
    def set_users(self, list):
        self.users = list

    def __str__(self):
        return f'id:{self.id} ip_name:{self.ip_name} users:{self.users}'

class Point(Record):
    id: int
    company_id: int
    city: str
    address: str
    name: str

    def update_data(self):
        self.id = self['id']
        self.company_id = self['company_id']
        self.city = self['city']
        self.address = self['address']
        self.name = self['name']

    def __str__(self):
        return f'"{self.name}" по адрессу, {self.city}, {self.address}'
    
async def get_keyboard(list: list):
    keybord_points = ReplyKeyboardBuilder()

    for i in range(len(list)):
        text = list[i].__str__()
        keybord_points.button(text=text)
    keybord_points.adjust(1,repeat=True)
    return keybord_points.as_markup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Торговые точки')

def find_all_indexes(input_str, substring):
    l2 = []
    length = len(input_str) 
    index = 0 
    while index < length: 
        i = input_str.find(substring, index) 
        if i == -1: 
            return l2 
        l2.append(i) 
        index = i + 1 
    return l2

class Order(Record):
    id: int
    company_id: int
    point_id: int
    bucket_id: int
    date_order: datetime
    summ: int

class Bucket(Record):
    id: int
    product_id: int

class Product(Record):
    id: int
    name: str

class ProductButton(CallbackData, prefix='product'):
    product_name: str
