import MySQLdb

from ajenti.com import *
from ajenti import apis


class MySQLDBBackend(Plugin):
    implements(apis.sql.IDBBackend)

    name = 'MySQL'

    conn = None
    cur = None

    def connect(self, host, login, password, db):
        self.conn = MySQLdb.connect(host=host, user=login, passwd=password, db=db)

    def disconnect(self):
        self.conn.close()

    def sql(self, query):
        res = []
        try:
            self.cur = self.conn.cursor()
            self.cur.execute(query)
            while True:
                row = self.cur.fetchone()
                if row is None:
                    break
                res.append(row)
            self.cur.close()
            return res
        except Exception as (c,e):
            return '%s (%s)' % (e,str(c))
