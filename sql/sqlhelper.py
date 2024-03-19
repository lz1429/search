import pymysql


class SQLHELPER(object):
    def __init__(self):
        # 读取配置文件
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='110120119',
                                    db='price_comparison_system')
        self.cursor = self.conn.cursor()

    def get_list(self, sql, args):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchall()
        return result

    def get_one(self, sql, args):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchone()
        return result

    def modify(self, sql, args):
        self.cursor.execute(sql, args)
        self.conn.commit()

    def multiple_modify(self, sql, args):
        self.connect()
        self.cursor.executemany(sql, args)
        self.conn.commit()

    def create(self, sql, args):
        self.cursor.execute(sql, args)
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        self.cursor.close()
        self.conn.close()
