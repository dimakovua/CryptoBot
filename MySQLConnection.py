import pymysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

class MySQLConnection:
    def __init__(self):
        self.host = DB_HOST
        self.port = int(DB_PORT)
        self.user = DB_USER
        self.passwd = DB_PASS
        self.db = DB_NAME
        self.connect = pymysql.Connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        self.cursor = self.connect.cursor()

    def __del__(self):
        self.connect.close()

    def connect_mysql(self):
        return pymysql.Connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
    
    def operate_database(self, command):
        # example select mysql version
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result
    
    def get_pairs(self, number):
        self.cursor.execute(f"SELECT name FROM Pairs ORDER BY priority DESC LIMIT {number};")
        result = self.cursor.fetchall()
        return result

    def use_pair(self, name):
        self.cursor.execute(f"SELECT * FROM Pairs WHERE name = '{name}';")
        if self.cursor.rowcount == 0:
            self.cursor.execute(f"INSERT INTO Pairs (name, priority) VALUES ('{name}', 1);")
        else:
            self.cursor.execute(f"UPDATE Pairs SET priority = priority + 1 WHERE name = '{name}';")
