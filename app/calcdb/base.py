import re
import psycopg2

from typing import List, Dict, Any

class DB(object):
    def __init__(self, conn: str):
        self.conn = psycopg2.connect(conn)
        self.cursor = self.conn.cursor()
        self.cursor.arraysize = 20000
       
    def close(self):
        self.conn.close()

    