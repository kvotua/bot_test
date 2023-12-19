from asyncpg import Record

class User(Record):
    user_id: int
    username: str
    firstname: str
    lastname: str

    def update_data(self):
        self.user_id=self['user_id']
        self.username=self['username']
        self.firstname=self['firstname']
        self.lastname=self['lastname']

    def __str__(self):
        return f'{self.user_id} {self.username} {self.firstname} {self.lastname}'
    