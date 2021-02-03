from . import base

from typing import List, Dict
    
class VisDB(base.DB):
    def reset_pwd(self, username: str, pwdhash: str) -> None:
        '''重置密码'''

        self.cursor.execute("""
            update auth_user set pwdhash=%s
            where username=%s
        """, (pwdhash, username))

        self.conn.commit()

        return