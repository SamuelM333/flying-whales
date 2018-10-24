from ldap3 import Server, Connection, ALL as ALL_INFO


def connect_to_ldap_server(host, dn, password):
    server = Server(host, get_info=ALL_INFO)
    conn = Connection(server, dn, password, auto_bind=True)
    return server, conn


class LDAPBind:
    def __init__(self, host, dn, password):
        self.host = host
        self.dn = dn
        self.password = password

    def __enter__(self):
        self.server = Server(self.host, get_info=ALL_INFO)
        self.conn = Connection(self.server, self.dn, self.password, auto_bind=True)
        return self.server, self.conn

    def __exit__(self, *args):
        self.conn.unbind()
