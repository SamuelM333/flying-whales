from flask_login import UserMixin
from ldap3 import Connection

from config import BASE_DN

users = {}


class User(UserMixin):
    def __init__(self, server, conn, username):
        self.server = server
        self.conn = conn
        self.username = username
        self.dn = ""

    def __repr__(self):
        return "Username: {}, DN: {}".format(self.username, self.dn)

    def get_id(self):
        return str(self.username)

    def try_login(self, password):
        if password is not None and password.strip() != "":
            if self.conn.search(BASE_DN, '(SamAccountName={})'.format(self.username)):
                if len(self.conn.entries) > 0:
                    user = self.conn.entries[0]
                    user_bind = Connection(self.server, user=user.entry_dn, password=password)
                    self.dn = user.entry_dn
                    users[self.username] = self
                    return user_bind.bind()

        return False
