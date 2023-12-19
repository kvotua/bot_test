from asyncpg import Record

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
    